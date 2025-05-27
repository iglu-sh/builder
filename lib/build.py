#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
from jinja2 import Environment, FileSystemLoader
from git import Repo

parser = argparse.ArgumentParser(description="Build a flake and publish it to an iglu-cache")
# Default params
parser.add_argument("--dir", type=str, default="./repo", help="The directory in witch the repo should be cloned into")

# Git params
parser.add_argument("--no-clone", action="store_true", help="Don't clone any repository")
parser.add_argument("--repository", type=str, help="The repository to clone")

# Bild params
parser.add_argument("--command", required=True, type=str, help="The repository to clone")

# Cachix params
parser.add_argument("--no-push", action="store_true", help="Don't push any result")
parser.add_argument("--target", type=str, help="URL of the cache with cache (https://caches.iglu.sh/default)")
parser.add_argument("--api-key", type=str, help="Authtoken for the cache")
parser.add_argument("--signing-key", type=str, help="key witch is used to sign the derivations")

args = parser.parse_args()

# Check args
if not args.no_clone and args.repository is None:
    parser.error("--repository is required if --no-clone is not set.")
if not args.no_push:
    if args.target is None:
        parser.error("--target is required if --no-push is not set.")
    if args.api_key is None:
        parser.error("--api-key is required if --no-push is not set.")
    if args.signing_key is None:
        parser.error("--signing-key is required if --no-push is not set.")

def prepare_cachix():
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
    template = env.get_template("cachix.dhall.j2")
    data = {
        "authToken": args.api_key,
        "hostname": "/".join(args.target.split("/")[0:-1]) + "/",
        "binaryCache": args.target.split("/")[-1],
        "secretKey": args.signing_key
    }

    cachix_config = template.render(data)
    with open(args.dir + "/cachix.dhall", "w") as f:
        f.write(cachix_config)

def clone():
    # TODO: Pull if exists insted of removing and recloning
    # TODO: Add option for auth
    # TODO: add ssh support
    if os.path.exists(args.dir):
        shutil.rmtree(args.dir)

    Repo.clone_from(args.repository, args.dir)

def build():
    # Create Dir if not exists
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)

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

        if(child.returncode != 0):
            exit(1)
    else:
        print("Invalid command! Command must start with \"nix\" or \"nix-build\"")
        exit(1)

def push():
    child = subprocess.Popen(
        ["cachix", "-c", "./cachix.dhall", "push", "default", "result"],
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

def main():
    if(not args.no_push):
        prepare_cachix()

    if(not args.no_clone):
        clone()
    build()
    push()

main()
