# Using buildpacks

## What is a buildpack and why use it?

here

## Steps to getting started

1. Install pack

```bash 
brew install buildpacks/tap/pack
```

2. Let's see what builder pack recommends us to use to build our image

```bash
pack builder suggest
```

3. We'll use the google image because it has python built in. Let's set the default builder image.

```bash
pack config default-builder gcr.io/buildpacks/builder:v1
```

4. Next, we need to create a Procfile, which essentially instructs the buildpack mechanism how we want to serve our application.
If we inspect our application, we'll see that we run our app using uvicorn, so all we need to do is to run the main.py script. 
Let's set that in a file called `Procfile`

Example:
```
web: python3 main.py
```

5. Now it's time to get our Docker image built.
 
```bash
pack build user-api
```

6. This will take a couple of minutes as the builder image is being pulled and it is building a new image to support our file.
Note that `user-api` is the name of the artifact image that will be built.
We mention this as in the next step we will be running a Docker image locally on our host to test.

7. Once the build is complete, it's time to run the Docker image locally as a container! Run the following command to start the container.
#get dynamo table name from CFN

```bash
docker run --rm --name userapi -e DYNAMO_TABLE=BuildEc2EnvironmentStack-UsersTable9725E9C8-15YOODVAKC49B -p 8080:8080 user-api
```

8. Let's test it!

```bash
curl -s localhost:8080/all_users | jq
```

9. With buildpacks, we were able to take our code and simply define how we want to run it in a Procfile. 
From this point, we could push this image and continue as is. But we may want to have more control, so let's create our own Dockerfile.

10. Walk through the dockerfile step by step:

  - We need to build from a base image. This is esentially how we are defining the operating system that our app will run on.
  - Next, we need to take 

11. Talk about copilot and how we can create our service. We can either use the existing vpc, or create a new one.

