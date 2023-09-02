#!/usr/bin/env python3

import os
import argparse
import subprocess

CWD = os.path.abspath(os.path.dirname(__file__))


def west(command: str, workdir="/"):
    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            f"--volume={CWD}/build/zmk:/root",
            f"--volume={CWD}/config:/workspace/config",
            f"--workdir=/root/{workdir}",
            "zmkfirmware/zmk-build-arm:3.2",
            "/bin/bash",
            "-c",
            command,
        ],
        check=True,
    )


def build(side: str, pristine=False):
    west(
        " ".join([
            "west",
            "build",
            "-p" if pristine else "",
            f"-d build/{side}",
            "-b nice_nano_v2",
            f"-- -DSHIELD=cradio_{side}",
            "-D ZMK_CONFIG=/workspace/config",
        ]),
        workdir="app",
    )


def reset():
    subprocess.run(
        ["cp", f"{CWD}/compiled/reset.uf2", "/Volumes/NICENANO"],
        check=True,
    )


def flash(side: str):
    subprocess.run(
        [
            "cp", f"{CWD}/build/zmk/app/build/{side}/zephyr/zmk.uf2",
            "/Volumes/NICENANO"
        ],
        check=True,
    )


def setup():
    """ Setup a local development environment.
        https://zmk.dev/docs/development/setup
    """
    if os.path.exists("build"):
        raise FileExistsError("`build` already exists")
    os.mkdir("build")
    subprocess.run(
        [
            "git",
            "clone",
            "https://github.com/zmkfirmware/zmk.git",
            "build/zmk",
        ],
        check=True,
    )
    west("west init -l app/")
    west("west update")


parser = argparse.ArgumentParser(
    prog="build.py",
    description="Build our ZMK firmware",
)
subparsers = parser.add_subparsers(dest="command")
build_parser = subparsers.add_parser("build")
build_parser.add_argument("--pristine", action="store_true")
build_parser.add_argument("--right", action="store_true")
build_parser.add_argument("--left", action="store_true")
subparsers.add_parser("reset")
subparsers.add_parser("setup")
flash_parser = subparsers.add_parser("flash")
flash_parser.add_argument("side", choices=["left", "right"])

args = parser.parse_args()
if args.command == "build":
    if not args.right or args.left:
        build("left", pristine=args.pristine)
    if not args.left or args.right:
        build("right", pristine=args.pristine)
if args.command == "reset":
    reset()
if args.command == "flash":
    flash(args.side)
if args.command == "setup":
    setup()
