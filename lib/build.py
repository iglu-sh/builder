#!/usr/bin/env python3

# --- exit codes ---
# 0: sucess
# 1: error
# 2: command not allowed

import argparse
import json
import os
import shutil
import subprocess
from jinja2 import Environment, FileSystemLoader
from git import Repo
from jsonschema import validate

# --- parsing ---
def parse_args() -> argparse.Namespace:
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

    # Substituter params
    parser.add_argument("--substituter", action="append", type=str, help="A substituter which is used during the build process")
    parser.add_argument("--trusted-key", action="append", type=str, help="A trusted public key of a substituter")

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
        if args.command is None:
            parser.error("--command is needed")
        if (args.substituter is None) != (args.trusted_key is None):
            parser.error("--substituter and --trusted-key have to be set or unset together")
        elif len(args.substituter) != len(args.trusted_key):
            parser.error("--substituter and --trusted-key must set equaly often")


    # Check if other args given if json is set
    invalid_args = [k for k, v in vars(args).items() if k not in ["json", "dir"] and v not in (None, False)]
    if args.json and len(invalid_args) > 1:
        print(invalid_args)
        parser.error("You can not set more params if --json is set.")

    return args


def parse_json_config(args: argparse.Namespace, json_str: str) -> argparse.Namespace:
    path = os.path.split(os.path.abspath(__file__))[0]

    try:                                   
        with open(path + '/../schemas/bodySchema.json') as f:
            jsonSchema = json.load(f)
    except Exception as e:
        print(str(e))                               
        exit(1)

    try:
        raw = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    validate(instance=raw, schema=jsonSchema)
    
    # Basic structure validation
    if "git" not in raw or "buildOptions" not in raw:
        raise ValueError("JSON must contain 'git' and 'buildOptions' keys")

    if not raw.get("git"):
        raw.setdefault("git", {})
    if not raw.get("buildOptions"):
        raw.setdefault("buildOptions", {})
    if not raw["buildOptions"].get("cachix"):
        raw["buildOptions"].setdefault("buildOptions", {})

    args.branch = raw["git"].setdefault("branch", None)
    args.git_user = raw["git"].setdefault("gitUsername", None)
    args.git_key = raw["git"].setdefault("gitKey", None)
    args.no_clone = raw["git"].setdefault("noClone", None)
    args.command = raw["buildOptions"].setdefault("command", None)
    args.no_push = not raw["buildOptions"]["cachix"].setdefault("push", True)
    args.api_key = raw["buildOptions"]["cachix"].setdefault("apiKey", None)
    args.signing_key = raw["buildOptions"]["cachix"].setdefault("signingKey", None)
    args.target = raw["buildOptions"]["cachix"].setdefault("target", None)
    args.substituter = raw["buildOptions"].setdefault("substituters", None)
    args.trusted_key = raw["buildOptions"].setdefault("trustedPublicKeys", None)

    return args

# --- Core ---
def clone(args: argparse.Namespace) -> None:
    # Set Repo url
    if not args.git_user is None and not args.git_key is None:
        repo = args.repository.replace("://", "://" + args.git_user + ":" + args.git_key + "@")
    else:
        repo = args.repository

    print("Checking if the repository is pulled already...")
    pulled = False
    # Check if repo direcotry already exists
    if os.path.exists(args.dir):
        remote_url= list(Repo(args.dir).remotes["origin"].urls)[0]

        # Pull Repo if remote is correct and delete it if not
        if remote_url == repo:
            print("Repository found! Pulling it...")
            Repo(args.dir).remotes['origin'].pull()
            pulled = True
        else:
            shutil.rmtree(args.dir)

    # Clone Repo if not pulled
    if not pulled:
        print("Repository not found! Cloning it...")
        print("Cloning repo: " + repo + "...")
        try:
            Repo.clone_from(repo, args.dir)
        except Exception as e:
            print(e)
            exit(1)

def build(args: argparse.Namespace) -> None:
    # Check if command start with nix or nix-build
    if args.command.split(" ")[0] in ["nix", "nix-build"]:
        # Set substituter option
        substituter_option = []
        if not args.substituter is None:
            substituter_option = [
                "--option",
                "extra-trusted-public-keys",
                " ".join(args.trusted_key),
                "--option",
                "extra-substituters",
                " ".join(args.substituter)
            ]
        print(args.command.split(" ") + ["--extra-experimental-features", "nix-command", "--extra-experimental-features", "flakes", "--eval-store", "/tmp"] + substituter_option)
        child = subprocess.Popen(
            args.command.split(" ") + ["--extra-experimental-features", "nix-command", "--extra-experimental-features", "flakes", "--eval-store", "/tmp"] + substituter_option,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=args.dir
        )

        if not child.stdout is None:
            for line in child.stdout:
                print(line, end='')

        child.wait()

        if(child.returncode != 0):
            exit(1)
    else:
        print("Invalid command! Command must start with \"nix\" or \"nix-build\"")
        exit(2)

def prepare_cachix(args: argparse.Namespace) -> None:
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

def push(args: argparse.Namespace) -> None:
    child = subprocess.Popen(
        ["cachix", "-c", "./cachix.dhall", "push", "default", "result"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=args.dir
    )

    if not child.stdout is None:
        for line in child.stdout:
            print(line, end='')

    child.wait()

    if(child.returncode != 0):
        exit(1)
# --- Main ---
def main() -> None:
    args = parse_args()
    
    if args.json != None:
        args = parse_json_config(args, args.json)

    if not os.path.exists(args.dir):
        os.makedirs(args.dir)

    if not args.no_clone:
        clone(args)

    build(args)

    if not args.no_push:
        prepare_cachix(args)
        push(args)

main()
