1) Build an environment to start that has our api service running on an EC2 host as a systemd unit.
2) Walk through how it's built and some of the challenges that come with running things this way
3) Talk about containerizing the app and the benefits that will come with containerization.
4) We get our feet wet by building our container images using buildpacks
5) Move to building our own Dockerfile, build and test it locally
6) copilot time - deploy our container image to ecs using copilot.


Copilot commands:

copilot app init

copilot env init --import-vpc-id vpc-0defc00f1982a2399 --name test --app migration

copilot svc init

Modify the manifest and add network configs:

environments:
  test:
    variables:
      DYNAMO_TABLE: UsersTable-test
    network:
      vpc:
        security_groups: ['sg-05f8a55186cfbc449']

TODO: in cdk code, make security group allowed to talk to self on 8080. 