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
# create user user_api_svc
# create directory /usr/local/user_api
# pull files down (github gist for now?)
# chmod +x
# systemd unit
useradd user_api_svc
mkdir -p /usr/local/user_api/models
echo 'DYNAMO_TABLE={dynamo_table.table_name}' >> /usr/local/user_api/config.ini
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
        