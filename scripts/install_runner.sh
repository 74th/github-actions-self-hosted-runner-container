#!/bin/bash
set -xe
UNAME_ARCH=$(uname -m)
if [ "${UNAME_ARCH}" = "aarch64" ]; then
    ARCH="arm64"
elif [ "${UNAME_ARCH}" = "x86_64" ]; then
    ARCH="amd64"
else
    echo "Unsupported architecture: ${UNAME_ARCH}"
    exit 1
fi

if [ -z "${RUNNER_VERSION}" ]; then
    RUNNER_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | jq -r '.tag_name' | sed 's/v//')
fi

curl -O -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${ARCH}-${RUNNER_VERSION}.tar.gz
tar xzf ./actions-runner-linux-${ARCH}-${RUNNER_VERSION}.tar.gz
