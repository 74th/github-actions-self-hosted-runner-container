#!/bin/bash
set -xe

env

if [ -z "${ACCESS_TOKEN}" ]; then
    echo "ACCESS_TOKEN is not set. Please set the ACCESS_TOKEN environment variable."
    exit 1
fi
if [ -z "${OWNER}" ]; then
    echo "OWNER is not set. Please set the OWNER environment variable."
    exit 1
fi
if [ -z "${REPO}" ]; then
    echo "REPO is not set. Please set the REPO environment variable."
    exit 1
fi
if [ -z "${GITHUB_API_URL}" ]; then
    GITHUB_API_URL="https://api.github.com"
fi
if [ -z "${GITHUB_URL}" ]; then
    GITHUB_URL="https://github.com"
fi
if [ -z "${RUNNER_NAME}" ]; then
    RUNNER_NAME=$(hostname)
fi

REG_TOKEN=$(curl -sX POST -H "Authorization: token ${ACCESS_TOKEN}" ${GITHUB_API_URL}/repos/${OWNER}/${REPO}/actions/runners/registration-token | jq .token --raw-output)
cd /home/runner/actions-runner
echo "setup Repository Runner"
./config.sh \
    --url ${GITHUB_URL}/${OWNER}/${REPO} \
    --unattended \
    --name ${RUNNER_NAME} \
    --token ${REG_TOKEN}

cleanup() {
    echo "Removing runner..."
    ./config.sh remove --token ${REG_TOKEN}
}

trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM

./run.sh & wait $!