#!/usr/bin/env python3

import os
import argparse
import subprocess
import sys

CWD = os.path.abspath(os.path.dirname(__file__))
ZMK_DIR = os.path.join(CWD, "build", "zmk")
DOCKER_IMAGE = "zmkfirmware/zmk-build-arm:4.1"
# Override via env var if your keyboard mounts elsewhere
FLASH_MOUNT = os.environ.get("ZMK_FLASH_MOUNT", "/media/kb")


def check_setup():
    if not os.path.exists(ZMK_DIR):
        print("error: build environment not found — run: python build.py setup", file=sys.stderr)
        sys.exit(1)


def west(command: str, workdir=""):
    subprocess.run(
        [
            "docker", "run", "--rm",
            f"--volume={ZMK_DIR}:/root",
            f"--volume={CWD}/config:/workspace/config",
            f"--workdir=/root/{workdir}",
            DOCKER_IMAGE,
            "/bin/bash", "-c", command,
        ],
        check=True,
    )


def build(side: str, pristine=False):
    check_setup()
    west(
        " ".join(filter(None, [
            "west build",
            "-p" if pristine else "",
            f"-d build/{side}",
            "-b nice_nano//zmk",
            f"-- -DSHIELD=cradio_{side}",
            "-DZMK_CONFIG=/workspace/config",
        ])),
        workdir="app",
    )


def flash(side: str):
    check_setup()
    src = os.path.join(ZMK_DIR, "app", "build", side, "zephyr", "zmk.uf2")
    if not os.path.exists(src):
        print(f"error: firmware not found at {src} — run build first", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(FLASH_MOUNT):
        print(f"error: {FLASH_MOUNT!r} not found — is the keyboard in bootloader mode?", file=sys.stderr)
        sys.exit(1)
    subprocess.run(["cp", src, FLASH_MOUNT], check=True)
    print(f"flashed {side} → {FLASH_MOUNT}")


def setup():
    if not os.path.exists(ZMK_DIR):
        subprocess.run(
            ["git", "clone", "https://github.com/zmkfirmware/zmk.git", ZMK_DIR],
            check=True,
        )
    else:
        print("zmk repo already present, skipping clone")

    west_config = os.path.join(ZMK_DIR, ".west", "config")
    if not os.path.exists(west_config):
        west("west init -l app/")
        west("west update")
    else:
        print("west already initialized, skipping")


parser = argparse.ArgumentParser(prog="build.py", description="Build ZMK firmware locally via Docker")
subparsers = parser.add_subparsers(dest="command")

build_parser = subparsers.add_parser("build", help="compile firmware")
build_parser.add_argument("--pristine", action="store_true", help="clean build")

flash_parser = subparsers.add_parser("flash", help="copy firmware to keyboard in bootloader mode")
flash_parser.add_argument("side", choices=["left", "right"])

subparsers.add_parser("setup", help="clone ZMK and initialize west (first-time only)")

args = parser.parse_args()

if args.command == "build":
    build("left", pristine=args.pristine)
    build("right", pristine=args.pristine)
elif args.command == "flash":
    flash(args.side)
elif args.command == "setup":
    setup()
else:
    parser.print_help()
