#!/usr/bin/env python3
import argparse
import os
import shutil
from git import Repo

parser = argparse.ArgumentParser(description="Clone a git repository")
parser.add_argument("--repo", required=True, type=str, help="The repository to clone")
parser.add_argument("--dir", type=str, default="./repo", help="The directory in witch the repo should be cloned into")

args = parser.parse_args()

if os.path.exists(args.dir):
    shutil.rmtree(args.dir)

Repo.clone_from(args.repo, args.dir)
