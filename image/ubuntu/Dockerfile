ARG UBUNTU_VERSION=24.04
FROM ubuntu:${UBUNTU_VERSION}

RUN groupadd -g 999 user && \
    useradd -m -g 999 user && \
    mkdir -p /home/runner/actions-runner

WORKDIR /home/runner/actions-runner

COPY scripts/ubuntu/install_runner_dependency.sh .
RUN bash ./install_runner_dependency.sh

COPY scripts/install_runner.sh .
RUN bash ./install_runner.sh

COPY scripts/run_runner.sh .
RUN mkdir -p /home/runner/actions-runner
RUN chown -R user:user /home/runner

USER user

ENTRYPOINT [ "bash", "./run_runner.sh" ]
