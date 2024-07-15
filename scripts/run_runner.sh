#!/bin/bash
set -xe

env

if [ -z "${RUNNER_ACCESS_TOKEN}" ]; then
    echo "RUNNER_ACCESS_TOKEN is not set. Please set the ACCESS_TOKEN environment variable."
    exit 1
fi
if [ -z "${RUNNER_OWNER}" ]; then
    echo "RUNNER_OWNER is not set. Please set the OWNER environment variable."
    exit 1
fi
if [ -z "${RUNNER_REPO}" ]; then
    echo "RUNNER_REPO is not set. Please set the REPO environment variable."
    exit 1
fi
if [ -z "${RUNNER_GITHUB_API_URL}" ]; then
    RUNNER_GITHUB_API_URL="https://api.github.com"
fi
if [ -z "${RUNNER_GITHUB_URL}" ]; then
    RUNNER_GITHUB_URL="https://github.com"
fi
ADDITIONAL_FLAGS_FLAGS=""

if [ -n "${RUNNER_NAME}" ]; then
    ADDITIONAL_FLAGS="${ADDITIONAL_FLAGS} --name ${RUNNER_NAME}"
fi
if [ -n "${RUNNER_GROUP}" ]; then
    ADDITIONAL_FLAGS="${ADDITIONAL_FLAGS} --runnergroup ${RUNNER_GROUP}"
fi
if [ -n "${RUNNER_LABELS}" ]; then
    ADDITIONAL_FLAGS="${ADDITIONAL_FLAGS} --labels ${RUNNER_LABELS}"
fi
if [ "${RUNNER_NO_DEFAULT_LABEL}" == "true" ]; then
    ADDITIONAL_FLAGS="${ADDITIONAL_FLAGS} --no-default-labels"
fi
if [ "${RUNNER_EPHEMERAL}" == "true" ]; then
    ADDITIONAL_FLAGS="${ADDITIONAL_FLAGS} --ephemeral"
fi
if [ "${RUNNER_REPLACE}" == "true" ]; then
    ADDITIONAL_FLAGS="${ADDITIONAL_FLAGS} --replace"
fi
if [ "${RUNNER_DISABLEUPDATE}" == "true" ]; then
    ADDITIONAL_FLAGS="${ADDITIONAL_FLAGS} --disableupdate"
fi
if [ "${RUNNER_WORK}" == "true" ]; then
    ADDITIONAL_FLAGS="${ADDITIONAL_FLAGS} --WROK"
fi

REG_TOKEN=$(curl -sX POST -H "Authorization: token ${RUNNER_ACCESS_TOKEN}" ${RUNNER_GITHUB_API_URL}/repos/${RUNNER_OWNER}/${RUNNER_REPO}/actions/runners/registration-token | jq .token --raw-output)
cd /home/runner/actions-runner
echo "setup Repository Runner"
./config.sh \
    --url ${RUNNER_GITHUB_URL}/${RUNNER_OWNER}/${RUNNER_REPO} \
    --unattended \
    ${ADDITIONAL_FLAGS} \
    --token ${REG_TOKEN}

cleanup() {
    echo "Removing runner..."
    ./config.sh remove --token ${REG_TOKEN}
}

trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM

./run.sh & wait $!