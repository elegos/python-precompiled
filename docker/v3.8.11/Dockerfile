#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.py"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

# This image should not be used alone.
# The main purpose is to compile a Python version
# in order to be copied into another environment.
#
# Example of usage might be to create AppImages that depend on Python

FROM buildpack-deps:buster

# ensure local python is preferred over distribution python
ENV PATH /usr/local/bin:$PATH

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

# extra dependencies (over what buildpack-deps already includes)
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
  libbluetooth-dev \
  tk-dev \
  uuid-dev \
  && rm -rf /var/lib/apt/lists/*

ENV GPG_KEY E3FF2839C048B25C084DEBE9B26995E310250568
ENV PYTHON_VERSION 3.8.11

RUN set -ex \
  \
  && wget -O python.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz" \
  && wget -O python.tar.xz.asc "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz.asc" \
  && export GNUPGHOME="$(mktemp -d)" \
  && gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$GPG_KEY" \
  && gpg --batch --verify python.tar.xz.asc python.tar.xz \
  && { command -v gpgconf > /dev/null && gpgconf --kill all || :; } \
  && rm -rf "$GNUPGHOME" python.tar.xz.asc \
  && mkdir -p /opt/python/${PYTHON_VERSION} \
  && mkdir -p /usr/src/python \
  && tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
  && rm python.tar.xz \
  \
  && cd /usr/src/python \
  && gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)" \
  && ./configure \
  --build="$gnuArch" \
  --enable-loadable-sqlite-extensions \
  --enable-optimizations \
  --enable-option-checking=fatal \
  --enable-shared \
  --with-system-expat \
  --with-system-ffi \
  --without-ensurepip \
  --prefix=/opt/python/${PYTHON_VERSION}/ \
  && make -j "$(nproc)" \
  && make install \
  && rm -rf /usr/src/python \
  && find /opt/python/${PYTHON_VERSION} -depth \
  \( \
  \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
  -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
  \) -exec rm -rf '{}' +

RUN ln -sr /opt/python/${PYTHON_VERSION} /opt/python/$(echo $PYTHON_VERSION | sed 's/\.[0-9]*$//')
RUN ln -sr /opt/python/${PYTHON_VERSION} /opt/python/$(echo $PYTHON_VERSION | sed 's/\.[0-9]\.[0-9]*$//')

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# Default entrypoint copies Python into the input path
# i.e. docker run --user "`id -u`:`id -g`" ... /usr/
ENTRYPOINT ["/entrypoint.sh"]
