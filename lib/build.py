#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import json
import collections.abc
from jinja2 import Environment, FileSystemLoader
from git import Repo

parser = argparse.ArgumentParser(description="Build a flake and publish it to an iglu-cache")
# Default params
parser.add_argument("--dir", type=str, default="/tmp/iglu-builder/repo", help="The directory in witch the repo should be cloned into")

# Git params
parser.add_argument("--no-clone", action="store_true", help="Don't clone any repository")
parser.add_argument("--repository", type=str, help="The repository to clone")
parser.add_argument("--branch", type=str, help="The repositorys branch to clone")
parser.add_argument("--git-user", type=str, help="The username to clone the repositorys")
parser.add_argument("--git-key", type=str, help="The key to clone the repositorys")

# Bild params
parser.add_argument("--command", type=str, help="The repository to clone")

# Cachix params
parser.add_argument("--no-push", action="store_true", help="Don't push any result")
parser.add_argument("--target", type=str, help="URL of the cache with cache (https://caches.iglu.sh/default)")
parser.add_argument("--api-key", type=str, help="Authtoken for the cache")
parser.add_argument("--signing-key", type=str, help="key witch is used to sign the derivations")

# JSON
parser.add_argument("--json", type=str, help="Input all settings via JSON")

args = parser.parse_args()

# Check args
if args.json is None:
    if not args.no_clone and args.repository is None:
        parser.error("--repository is required if --no-clone is not set.")
    if not args.no_push:
        if args.target is None:
            parser.error("--target is required if --no-push is not set.")
        if args.api_key is None:
            parser.error("--api-key is required if --no-push is not set.")
        if args.signing_key is None:
            parser.error("--signing-key is required if --no-push is not set.")
    if not args.command is None:
        parser.error("--command is needed")

# Check if other args given if json is set
invalid_args = [k for k, v in vars(args).items() if k not in ["json", "dir"] and v not in (None, False)]
if args.json and len(invalid_args) > 1:
    print(invalid_args)
    parser.error("You can not set more params if --json is set.")

def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def parse_json():
    json_data = json.loads(args.json)
    json_schema= {
        "git": {
            "repository": None,
            "branch": None,
            "gitUsername": None,
            "gitKey": None,
            "requiresAuth": None,
            "noClone": None,
        },
        "buildOptions": {
            "cores": None,
            "maxJobs": None,
            "keep_going": None,
            "extraArgs": None,
            "substituters": None,
            "trustedPublicKeys": None,
            "command": None,
            "cachix": {
                "push": None,
                "target": None,
                "apiKey": None,
                "signingKey": None
            }
        }
    }
    json_data = update(json_schema, json_data)
    args.repository = json_data["git"]["repository"]
    args.branch = json_data["git"]["branch"]
    args.git_user = json_data["git"]["gitUsername"]
    args.git_key = json_data["git"]["gitKey"]
    args.no_clone = json_data["git"]["noClone"]
    args.command = json_data["buildOptions"]["command"]
    args.no_push = not json_data["buildOptions"]["cachix"]["push"]
    args.api_key = json_data["buildOptions"]["cachix"]["apiKey"]
    args.signing_key = json_data["buildOptions"]["cachix"]["signingKey"]
    args.target = json_data["buildOptions"]["cachix"]["target"]

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

    if(child.returncode != 0):
        exit(1)

def main():
    # Create Dir if not exists
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)

    # parse json if given
    if(args.json != None):
        parse_json()

    if(not args.no_clone):
        clone()
    
    if(not args.no_push):
        prepare_cachix()

    build()
    push()

main()
