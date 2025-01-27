# Git Hub Actions Self-Hosted Runner container image

## feature

- stand alone image
- run as non-root user

## Simple way

To use it, you need a GitHub Personal Access Token. Please activate and create the following

- repo
- workflow
- admin:org

Running the container will launch GitHub Actions Self-hosted Runner.

```
docker run --rm -i \
  -e RUNNER_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  -e RUNNER_OWNER=74th \
  -e RUNNER_REPO=github-actions-self-hosted-runner-container \
  ghcr.io/74th/github-actions-self-hosted-runner-container/debian-amd64:bookworm-slim
```

## Configuration

The script [run_runner.sh](./scripts/run_runner.sh) requires the following environment variables. Please enter these environment variables and start the container.

| name                      | required | description                           | runner config.sh flag | example                                       |
| ------------------------- | -------- | ------------------------------------- | --------------------- | --------------------------------------------- |
| `RUNNER_ACCESS_TOKEN`     | required | GitHub personal access token          |                       | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`    |
| `RUNNER_OWNER`            | required | owner of the repository               |                       | `74th`                                        |
| `RUNNER_REPO`             | required | repository name                       |                       | `github-actions-self-hosted-runner-container` |
| `RUNNER_GROUP`            | optional | runner group name                     | `--group`             | `deployer`                                    |
| `RUNNER_LABELS`           | optional | label                                 | `--labels`            | `arm64`                                       |
| `RUNNER_NO_DEFAULT_LABEL` | optional | no default label, ex:arm64            | `--no-default-labels` | `true`                                        |
| `RUNNER_RUNNER_NAME`      | optional | Runner name                           | `--name`              | default: `hostname`                           |
| `RUNNER_WORK`             | optional | workdir                               | `--work`              | default: `_work`                              |
| `RUNNER_REPLACE`          | optional | replace existing runner the same name | `--replace`           | `true`                                        |
| `RUNNER_DISABLEUPDATE`    | optional | disable update                        | `--disableupdate`     | `true`                                        |
| `RUNNER_EPHEMERAL`        | optional | ephemeral                             | `--ephemeral`         | `true`                                        |
| `RUNNER_GITHUB_API_URL`   | optional | GitHub API URL                        |                       | default: `https://api.github.com`             |
| `RUNNER_GITHUB_URL`       | optional | GitHub URL                            |                       | default: `https://github.com`                 |

## Image URL

- debian:bookworm-slim
  - `ghcr.io/74th/github-actions-self-hosted-runner-container/debian:latest`
  - `ghcr.io/74th/github-actions-self-hosted-runner-container/debian:bookworm-slim`
- debian:buster-slim
  - `ghcr.io/74th/github-actions-self-hosted-runner-container/debian:bookworm-slim`
- ubuntu:24.04
  - `ghcr.io/74th/github-actions-self-hosted-runner-container/ubuntu:24.04`
  - `ghcr.io/74th/github-actions-self-hosted-runner-container/ubuntu:latest`
- ubuntu:22.04
  - `ghcr.io/74th/github-actions-self-hosted-runner-container/ubuntu:22.04`

## scripts URL

- install dependency
  - debian: [https://raw.githubusercontent.com/74th/github-actions-self-hosted-runner-container/main/scripts/debian/install_runner_dependency.sh](./scripts/debian/install_runner_dependency.sh)
  - ubuntu: [https://raw.githubusercontent.com/74th/github-actions-self-hosted-runner-container/main/scripts/ubuntu/install_runner_dependency.sh](./scripts/ubuntu/install_runner_dependency.sh)
- install runner
  - [https://raw.githubusercontent.com/74th/github-actions-self-hosted-runner-container/main/scripts/install_runner.sh](./scripts/install_runner.sh)
- run runner
  - [https://raw.githubusercontent.com/74th/github-actions-self-hosted-runner-container/main/scripts/run_runner.sh](./scripts/run_runner.sh)

## Use cases

### Use as base image

```Dockerfile
FROM ghcr.io/74th/github-actions-self-hosted-runner-container/debian-arm64:bookworm-slim

USER root

RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/arm64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /bin/

USER user
```

### Use as side car image

example of kubernetes

```yml
# deploy
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
        - name: app
          image: hogeapp
          ports:
            - containerPort: 8080
        - name: actions-runner
          image: ghcr.io/74th/github-actions-self-hosted-runner-container/debian:latest
          envFrom:
            - secretRef:
                name: access-token-env
          env:
            - name: OWNER
              value: 74th
            - name: REPO
              value: github-actions-self-hosted-runner-container
```

### Add scripts your Dockerfile

```Dockerfile
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
```
