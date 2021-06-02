from aws_cdk import (
    core as cdk,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
    aws_dynamodb as dynamodb
)


class BuildEc2EnvironmentStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Will create VPC, spanning two AZ's, private and public with NAT Gateways
        _vpc = ec2.Vpc(self, "DemoVPC")
        
        dynamo_table = dynamodb.Table(
            self, "UsersTable",
            partition_key=dynamodb.Attribute(name="first_name", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="last_name", type=dynamodb.AttributeType.STRING),
        )
        
        # This is to ensure that when we destroy, the table doesn't stick around
        dynamo_table.add_removal_policy(cdk.RemovalPolicy.DESTROY)
        
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
wget https://gist.githubusercontent.com/adamjkeller/cb2dfcd2ad6c6dc74d02c83759f2a1c5/raw/93b65f6b11d07574667d636678e7716b805a8097/setup.sh
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
        
        asg.add_to_role_policy(ssm_session_manager_policy)
        dynamo_table.grant_read_write_data(asg.role)
        