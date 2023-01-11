#!/usr/bin/env python3
import os
import aws_cdk as cdk

from aws_cdk import App, Stack
from build_ec2_environment.build_ec2_environment_stack import BuildEc2EnvironmentStack


app = cdk.App()
BuildEc2EnvironmentStack(app, "BuildEc2EnvironmentStack", deploy_env='test')

app.synth()
