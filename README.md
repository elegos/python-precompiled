# Python precompiled ready-to-copy docker images

This project aims to daily build docker images published on Docker Hub with the latest Python 3.x versions (3.6+).

## How it works
The CI github workflow runs update.py, which finds the latest Python 3.x versions (the latest patch for each minor),
builds the relative image and publishes it under giacomofurlan/python-precompiled:v3.x.y

## Docker images
The produced images have a default entrypoint (`/entrypoint.sh`) which will copy the files in the given directory

## Example usate

### Copy to host directory

```bash
PYTHON_VERSION="3.9.4" # See the image tags for a complete list
docker run --rm -ti \
  --volume "$(pwd)/python":/opt/out
  giacomofurlan/python-precompiled:v${PYTHON_VERSION} \
  /opt/out
```

### Copy to a shared volume
```bash
docker volume create python-3.9.4

docker run --rm -ti \
  --volume python-3.9.4:/opt/out \
  giacomofurlan/python-precompiled:v3.9.4 \
  /opt/out

docker run --rm -ti \
  --volume python-3.9.4:/opt/AppDir/usr
  my_image \
  my_command

docker volume rm python-3.9.4
```

### Use as base image and copy the compiled files somewhere useful

```Dockerfile
FROM giacomofurlan/python-precompiled:v3.9.4

# Prepare an AppDir of an AppImage
RUN mkdir -p /opt/AppDir/usr \
  && /entrypoint.sh /opt/AppDir/usr

# Alternative
RUN mkdir -p /opt/AppDir/usr \
  && cp -r /opt/python/3.9.4/* /opt/AppDir/usr/

# Files are in /opt/python/{major}.{minor}.{patch}
# There are symlinks to it:
# - /opt/python/3.{minor}
# - /opt/python/3
```
