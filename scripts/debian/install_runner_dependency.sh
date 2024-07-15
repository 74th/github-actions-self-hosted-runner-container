#!/bin/bash
set -xe
apt-get update
apt-get install -y \
    curl \
    jq \
    ca-certificates \
    git \
    libicu-dev