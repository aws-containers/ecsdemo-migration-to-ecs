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

3. We'll use the google image because it has python built in. Time to build a docker image!

```bash
pack build user-api --path ./ --builder gcr.io/buildpacks/builder:v1
```

