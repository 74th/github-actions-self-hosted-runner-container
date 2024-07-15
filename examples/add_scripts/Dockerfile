FROM python:3.12-slim

RUN groupadd -g 999 user && \
    useradd -m -g 999 user && \
    mkdir -p /home/runner/actions-runner

WORKDIR /home/runner/actions-runner

ADD https://raw.githubusercontent.com/74th/github-actions-self-hosted-runner-container/main/scripts/debian/install_runner_dependency.sh .
RUN bash ./install_runner_dependency.sh

ADD https://raw.githubusercontent.com/74th/github-actions-self-hosted-runner-container/main/scripts/install_runner.sh .
RUN bash ./install_runner.sh

ADD https://raw.githubusercontent.com/74th/github-actions-self-hosted-runner-container/main/scripts/run_runner.sh .

RUN chown -R user:user /home/runner

USER user

ENTRYPOINT [ "bash", "./run_runner.sh" ]
