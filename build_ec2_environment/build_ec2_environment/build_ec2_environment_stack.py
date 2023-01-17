import aws_cdk as cdk

from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
    aws_dynamodb as dynamodb
)

class BuildEc2EnvironmentStack(cdk.Stack):

    def __init__(self, scope: cdk.App, construct_id: str, deploy_env: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.deploy_env = deploy_env

        # Will create VPC, spanning two AZ's, private and public with NAT Gateways
        _vpc = ec2.Vpc(self, "DemoVPC")
        
        dynamo_table = dynamodb.Table(
            self, "UsersTable",
            table_name=f"UsersTable-{self.deploy_env}",
            partition_key=dynamodb.Attribute(name="first_name", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="last_name", type=dynamodb.AttributeType.STRING),
        )
        
        # This is to ensure that when we destroy, the table doesn't stick around
        dynamo_table.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        
        ssm_session_manager_policy = iam.PolicyStatement(
            actions=[
                "ssmmessages:CreateControlChannel",
                "ssmmessages:CreateDataChannel",
                "ssmmessages:OpenControlChannel",
                "ssmmessages:OpenDataChannel",
                "s3:GetEncryptionConfiguration",
                "ssmmessages:CreateControlChannel",
                "ssmmessages:CreateDataChannel",
                "ssmmessages:OpenControlChannel",
                "ssmmessages:OpenDataChannel",
                "s3:GetEncryptionConfiguration",
                "ec2messages:AcknowledgeMessage",
                "ec2messages:DeleteMessage",
                "ec2messages:FailMessage",
                "ec2messages:GetEndpoint",
                "ec2messages:GetMessages",
                "ec2messages:SendReply",
                "ssmmessages:CreateControlChannel",
                "ssmmessages:CreateDataChannel",
                "ssmmessages:OpenControlChannel",
                "ssmmessages:OpenDataChannel",
                "ssm:DescribeAssociation",
                "ssm:GetDeployablePatchSnapshotForInstance",
                "ssm:GetDocument",
                "ssm:DescribeDocument",
                "ssm:GetManifest",
                "ssm:GetParameter",
                "ssm:GetParameters",
                "ssm:ListAssociations",
                "ssm:ListInstanceAssociations",
                "ssm:PutInventory",
                "ssm:PutComplianceItems",
                "ssm:PutConfigurePackageResult",
                "ssm:UpdateAssociationStatus",
                "ssm:UpdateInstanceAssociationStatus",
                "ssm:UpdateInstanceInformation"
            ],
            resources=["*"]
        )
        
        user_data = ec2.UserData.custom(f"""#!/usr/bin/env bash
        
# Pulling down the code and creating necessary folders/user
wget https://raw.githubusercontent.com/aws-containers/ecsdemo-migration-to-ecs/main/setup.sh
bash -x ./setup.sh

# Create systemd unit
cat << EOF >> /etc/systemd/system/user-api.service
[Unit]
Description=User API
After=network.target
[Service]
Type=simple
Restart=always
RestartSec=5
User=root
Environment=DYNAMO_TABLE={dynamo_table.table_name}
WorkingDirectory=/usr/local/user_api
ExecStart=/usr/bin/python3 main.py
EOF

systemctl enable user-api.service
systemctl start user-api.service
""")
        
        asg = autoscaling.AutoScalingGroup(
            self, "ApplicationASG",
            instance_type=ec2.InstanceType('t3.small'),
            machine_image=ec2.MachineImage.latest_amazon_linux(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                user_data=user_data
            ),
            vpc=_vpc
        )
        
        asg.connections.security_groups[0].add_ingress_rule(
            peer=asg.connections.security_groups[0],
            connection=ec2.Port(
                protocol=ec2.Protocol.TCP,
                string_representation="Self 8080",
                from_port=8080,
                to_port=8080
            )
        )
        
        asg.add_to_role_policy(ssm_session_manager_policy)
        dynamo_table.grant_full_access(asg.role)
        
        cdk.CfnOutput(
            self, "DynamoDBTableName",
            value=dynamo_table.table_name, 
            description="Users DynamoDB table", 
            export_name="UserAPIDynamoDBTable"
        )