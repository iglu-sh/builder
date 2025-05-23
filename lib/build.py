#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess

parser = argparse.ArgumentParser(description="Build a flake")
parser.add_argument("--command", required=True, type=str, help="The repository to clone")
parser.add_argument("--dir", type=str, default="./repo", help="The directory in witch the flake is")

args = parser.parse_args()

if not os.path.exists(args.dir):
    print("Directory does not exist")
    exit(1)

# Check if command start with nix or nix-build
if args.command.split(" ")[0] in ["nix", "nix-build"]:
    child = subprocess.Popen(
        args.command.split(" "),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=args.dir
    )

    for line in child.stdout:
        print(line, end='')

    child.wait()

    #child = subprocess.run(args.command.split(" "), shell=False, cwd=args.dir, text=True)
    if(child.returncode != 0):
        exit(1)
else:
    print("Invalid command! Command must start with \"nix\" or \"nix-build\"")
    exit(1)
