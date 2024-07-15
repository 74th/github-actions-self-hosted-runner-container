import os
import shlex
from pathlib import Path
import argparse
import subprocess

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", None)

ROOT_DIR = Path(__file__).resolve().parent.parent

def print_cmd(cmd: list[str]) -> None:
    if ACCESS_TOKEN is None:
        print(shlex.join(map(str, cmd)))
    else:
        print(shlex.join(map(str, cmd)).replace(ACCESS_TOKEN, "****"))

def test_add_scripts() -> None:
    tag = "example-add-script"

    cmd = [
        "docker",
        "build",
        "-t",
        tag,
        "."
    ]
    cwd = ROOT_DIR / "examples" / "add_scripts"
    print_cmd(cmd)
    subprocess.run(cmd, cwd=str(cwd), check=True)

    assert ACCESS_TOKEN

    cmd = [
        "docker",
        "run",
        "--rm",
        "-i",
        "-e",
        F"RUNNER_ACCESS_TOKEN={ACCESS_TOKEN}",
        "-e",
        "RUNNER_OWNER=74th",
        "-e",
        "RUNNER_NAME=example-add-script",
        "RUNNER_REPO=github-actions-self-hosted-runner-container",
        tag]
    print_cmd(cmd)
    subprocess.run(cmd, cwd=str(cwd), check=True)

def test_as_base_image() -> None:
    tag = "example-as-base-image"

    cmd = [
        "docker",
        "build",
        "-t",
        tag,
        "."
    ]
    cwd = ROOT_DIR / "examples" / "as_base_image"
    print_cmd(cmd)
    subprocess.run(cmd, cwd=str(cwd), check=True)

    assert ACCESS_TOKEN

    cmd = [
        "docker",
        "run",
        "--rm",
        "-i",
        "-e",
        F"RUNNER_ACCESS_TOKEN={ACCESS_TOKEN}",
        "-e",
        "RUNNER_OWNER=74th",
        "-e",
        "RUNNER_REPO=github-actions-self-hosted-runner-container",
        "-e",
        "RUNNER_NAME=example-as-base-image",
        tag]
    print_cmd(cmd)
    subprocess.run(cmd, cwd=str(cwd), check=True)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", required=True, help="test name")
    args = parser.parse_args()

    test_names = args.test.split(",")

    for test_name in test_names:
        if test_name == "add_scripts":
            test_add_scripts()
        if test_name == "as_base_image":
            test_as_base_image()

if __name__ == "__main__":
    main()
