import os
import subprocess
import sys
import requests

KTLINT_VER = "1.7.1"
KTLINT_JAR = os.path.join(os.path.expanduser("~/.cache/pre-commit"), "ktlint")
KTLINT_TMP = os.path.join(os.path.expanduser("~/.cache/pre-commit"), "ktlint.tmp")
DOWNLOAD_URL = "https://github.com/pinterest/ktlint/releases/download/{}/ktlint"


def run_command(command):
    try:
        return 0, subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True,
        ).decode("utf-8")
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output.decode("utf-8")


def download_ktlint_if_not_found():
    if os.path.isfile(KTLINT_JAR):
        return
    r = requests.get(DOWNLOAD_URL.format(KTLINT_VER), stream=True)
    with open(KTLINT_TMP, "wb") as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)
    os.rename(KTLINT_TMP, KTLINT_JAR)


def get_tracked_kotlin_files():
    try:
        output = subprocess.check_output(
            "git ls-files '*.kt' '*.kts'", shell=True
        ).decode().splitlines()
        return output
    except subprocess.CalledProcessError:
        return []


def run_ktlint():
    download_ktlint_if_not_found()
    kotlin_files = get_tracked_kotlin_files()

    if not kotlin_files:
        print("No tracked Kotlin files found.")
        return 0

    files_str = " ".join(f'"{f}"' for f in kotlin_files)
    command = f"java --enable-native-access=ALL-UNNAMED -jar {KTLINT_JAR} --format {files_str}"
    ret_code, output = run_command(command)

    if output:
        print(output)
        return 1

    return ret_code


if __name__ == "__main__":
    sys.exit(run_ktlint())
