FROM ghcr.io/74th/github-actions-self-hosted-runner-container/debian-arm64:bookworm-slim

USER root

RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/arm64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /bin/

USER user