#!env python3
from dataclasses import dataclass
import time
import github
import uuid
import signal
import os
import shlex
from pathlib import Path
import subprocess
import sys
import argparse

SUPPORT_DISTROS = ["ubuntu", "debian"]
ROOT_DIR = Path(__file__).resolve().parent.parent


@dataclass
class Runner:
    name: str
    status: str


def get_image_tag(distro: str, distro_version: str, arch: str | None) -> str:
    tag = f"github-actions-self-hosted-runner-{distro}:{distro_version}"
    if arch:
        tag += f"-{arch}"
    return tag


def get_docker_platform_from_arch(arch: str | None) -> str:
    if arch in ["x64", "amd64", "x86_64"]:
        return "linux/amd64"
    if arch in ["arm64", "aarch64"]:
        return "linux/arm64"
    else:
        print(f"unknown architecture:{arch}")
        print("supported architectures: x64, arm64")
        sys.exit(1)


def build_container(
    distro: str, distro_version: str, engine: str, arch: str | None
) -> bool:
    print("[build]", f"start distro:{distro} distro_version:{distro_version}")

    os.chdir(ROOT_DIR)

    tag = get_image_tag(distro, distro_version, arch)
    dockerfile = ROOT_DIR / "image" / distro / "Dockerfile"

    if engine == "docker":
        cmd = ["docker", "buildx", "build", "--output=type=docker"]
    else:
        cmd = [engine, "build"]
    if arch:
        cmd += ["--platform", get_docker_platform_from_arch(arch)]

    cmd += [
        "-f",
        dockerfile,
        "-t",
        tag,
        ROOT_DIR,
        "--build-arg",
        f"DISTRO_VERSION={distro_version}",
    ]
    print("[build]", shlex.join(map(str, cmd)))

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("[build]", "build successed")
        return True

    print("[build]", "build filed")
    return False


def test_run_container(
    distro: str,
    distro_version: str,
    engine: str,
    arch: str | None,
    repo_owner: str,
    repo_name: str,
    check: bool = False,
) -> bool:
    access_token = os.environ.get("ACCESS_TOKEN", None)
    if not access_token:
        print("ACCESS_TOKEN is required")
        sys.exit(1)

    print("[test]", "start test run")

    runner_name = "test-" + uuid.uuid4().hex[:8]
    tag = get_image_tag(distro, distro_version, arch)

    cmd = [engine, "run"]

    if arch:
        cmd += ["--platform", get_docker_platform_from_arch(arch)]

    cmd += [
        "-i",
        "--rm",
        "--name",
        runner_name,
        "-e",
        f"ACCESS_TOKEN={access_token}",
        "-e",
        f"OWNER={repo_owner}",
        "-e",
        f"REPO={repo_name}",
        "-e",
        f"RUNNER_NAME={runner_name}",
        tag,
    ]
    print(shlex.join(map(str, cmd)).replace(access_token, "****"))

    p = subprocess.Popen(cmd)

    def receive_signal(signum, _):
        print("interupted")
        p.send_signal(signal.SIGINT)

    signal.signal(signal.SIGINT, receive_signal)
    signal.signal(signal.SIGTERM, receive_signal)

    if check:
        cl = github.Github(auth=github.Auth.Token(access_token))
        repo_api = cl.get_repo(f"{repo_owner}/{repo_name}")

        try:
            time.sleep(5)

            if p.returncode is not None:
                print("[test]", f"exit code: {p.returncode}")
                sys.exit(1)

            for _ in range(10):
                try:
                    p.wait(timeout=3)
                    print("[test]", f"stopped container detected: {p.returncode}")
                    return False
                except subprocess.TimeoutExpired:
                    pass

                print("[test]", "check runner...")

                runners = repo_api.get_self_hosted_runners()

                for runner in runners:
                    if runner.name == runner_name:
                        print(
                            "[test]",
                            f"runner {runner_name} found, status: {runner.status}",
                        )
                        if runner.status == "online":
                            print("[test]", "online runner found")
                            return True

            else:
                print("[test]", "online runner not found")
                return False

        finally:
            try:
                p.wait(timeout=0.1)
            except subprocess.TimeoutExpired:
                print("[test]", "stop container")
                subprocess.run([engine, "stop", runner_name])

    else:
        p.wait()

        print("[test]", f"exit code:{p.returncode}")

    print("[test]", "test result: ", "success" if p.returncode == 0 else "failed")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--engine", default="docker", help="container engine")
    parser.add_argument("-a", "--arch", help="architecture [amd64, x64]")
    parser.add_argument("-d", "--distro", required=True, help="linux distribution name")
    parser.add_argument("-o", "--owner", default="74th", help="repository owner")
    parser.add_argument(
        "-r",
        "--repo",
        default="github-actions-self-hosted-runner-container",
        help="repository name",
    )
    parser.add_argument(
        "-v", "--distro-version", default="latest", help="distribution version"
    )
    parser.add_argument("--test", action="store_true", help="run container")
    parser.add_argument("--test-full", action="store_true", help="run container and")
    args = parser.parse_args()

    engine = args.engine
    arch = args.arch
    distro = args.distro
    repo_owner = args.owner
    repo_name = args.repo
    distro_version = args.distro_version
    is_run_test = args.test
    is_test_check = False
    if args.test_full:
        is_run_test = True
        is_test_check = True

    if distro not in SUPPORT_DISTROS:
        print(f"unsupported distribution: {distro}")
        print("supported distributions: " + ", ".join(SUPPORT_DISTROS))
        sys.exit(1)

    ok = build_container(
        distro=distro,
        distro_version=distro_version,
        engine=engine,
        arch=arch,
    )
    if not ok:
        sys.exit(1)

    if is_run_test:
        ok = test_run_container(
            distro=distro,
            distro_version=distro_version,
            engine=engine,
            arch=arch,
            repo_owner=repo_owner,
            repo_name=repo_name,
            check=is_test_check,
        )
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
