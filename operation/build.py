#!env python3
from dataclasses import dataclass
import time
import urllib3
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


def get_image_tag(distro: str, distro_version: str) -> str:
    return f"github-actions-self-hosted-runner-{distro}:{distro_version}"


def build_container(distro: str, distro_version: str, engine: str):
    print(f"start distro:{distro} distro_version:{distro_version}")

    os.chdir(ROOT_DIR)

    tag = get_image_tag(distro, distro_version)
    dockerfile = ROOT_DIR / "image" / distro / "Dockerfile"

    cmd = [engine, "build", "-f", dockerfile, "-t", tag, ROOT_DIR]
    print(shlex.join(map(str, cmd)))

    subprocess.run(cmd)


def _get_github_runners(repo_owner: str, repo_name: str, access_token: str) -> list[Runner]:
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runners"
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    res = urllib3.request("GET", url, headers=headers)
    if res.status == 200:
        res_body = res.json()
        return list(map(lambda x: Runner(x["name"], x["status"]), res_body["runners"]))
    else:
        raise Exception(f"failed to get runners: {res.status}")




def test_run_container(
    distro: str,
    distro_version: str,
    engine: str,
    repo_owner: str,
    repo_name: str,
    check: bool = False,
) -> bool:
    access_token = os.environ.get("ACCESS_TOKEN", None)
    if not access_token:
        print("ACCESS_TOKEN is required")
        sys.exit(1)

    print("[test] start test run")

    runner_name = "test-" + uuid.uuid4().hex[:8]
    tag = get_image_tag(distro, distro_version)

    cmd = [
        engine,
        "run",
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
    signal.signal(signal.SIGTERM,receive_signal)

    if check:
        try:
            time.sleep(5)

            if p.returncode is not None:
                print(f"[test] exit code: {p.returncode}")
                sys.exit(1)

            for _ in range(10):
                if p.returncode is not None:
                    print(f"[test] stopped container detected: {p.returncode}")
                    return False

                print("[test] check runner...")

                runners = _get_github_runners(repo_owner, repo_name, access_token)

                for runner in runners:
                    if runner.name == runner_name:
                        print(f"[test] runner {runner_name} found, status: {runner.status}")
                        if runner.status == "online":
                            print("[test] online runner found")
                            return True

                time.sleep(3)

            else:
                print("[test] online runner not found")
                return False

        finally:
            if p.returncode is None:
                print("[test] stop container")
                subprocess.run([engine, "stop", runner_name])

    else:
        p.wait()

        print(f"exit code:{p.returncode}")

    print("[test] test result: ", "success" if p.returncode == 0 else "failed")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--engine", default="docker", help="container engine")
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

    build_container(distro, distro_version, engine)

    if is_run_test:
        ok = test_run_container(distro, distro_version, engine, repo_owner, repo_name, is_test_check)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
