Skip to content
This repository
Search
Pull requests
Issues
Marketplace
Explore
 @sunilmamillapall1
Sign out
29
5 14 openbmc/openbmc-build-scripts
 Code  Issues 4  Pull requests 0  Projects 0  Wiki  Insights
openbmc-build-scripts/scripts/build-qemu-robot-docker.sh
7a88f29  on Jan 29
@geissonator geissonator Allow a different qemu-system-arm to be passed to test scripts
@geissonator @rahulmah @saqibkh
     
Executable File  89 lines (76 sloc)  1.86 KB
#!/bin/bash -xe
#
# Build the required docker image to run QEMU and Robot test cases
#
#  Parameters:
#   parm1:  <optional, the name of the docker image to generate>
#            default is openbmc/ubuntu-robot-qemu

set -uo pipefail

DOCKER_IMG_NAME=${1:-"openbmc/ubuntu-robot-qemu"}

# Determine our architecture, ppc64le or the other one
if [ $(uname -m) == "ppc64le" ]; then
    DOCKER_BASE="ppc64le/"
else
    DOCKER_BASE=""
fi

################################# docker img # #################################
# Create docker image that can run QEMU and Robot Tests
Dockerfile=$(cat << EOF
FROM ${DOCKER_BASE}ubuntu:latest
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -yy \
    debianutils \
    gawk \
    git \
    python \
    python-dev \
    python-setuptools \
    python3 \
    python3-dev \
    python3-setuptools \
    socat \
    texinfo \
    wget \
    gcc \
    libffi-dev \
    libssl-dev \
    xterm \
    mwm \
    ssh \
    vim \
    iputils-ping \
    sudo \
    cpio \
    unzip \
    diffstat \
    expect \
    curl \
    build-essential \
    libpixman-1-0 \
    libglib2.0-0 \
    pysnmp
RUN easy_install \
    tox \
    pip \
    requests
RUN pip install \
    json2yaml \
    robotframework \
    robotframework-requests \
    robotframework-sshlibrary \
    robotframework-scplibrary
RUN wget https://sourceforge.net/projects/ipmitool/files/ipmitool/1.8.18/ipmitool-1.8.18.tar.bz2
RUN tar xvfj ipmitool-*.tar.bz2
RUN ./ipmitool-1.8.18/configure
RUN make
RUN make install
RUN grep -q ${GROUPS} /etc/group || groupadd -g ${GROUPS} ${USER}
RUN grep -q ${UID} /etc/passwd || useradd -d ${HOME} -m -u ${UID} -g ${GROUPS} \
                    ${USER}
USER ${USER}
ENV HOME ${HOME}
RUN /bin/bash
EOF
)

################################# docker img # #################################

# Build above image
docker build -t ${DOCKER_IMG_NAME} - <<< "${Dockerfile}"
© 2018 GitHub, Inc.
Terms
Privacy
Security
Status
Help
Contact GitHub
API
Training
Shop
Blog
About
