#!/usr/bin/env python3
import argparse, subprocess, sys

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--topics", default="")
    args = p.parse_args()

    cmd = ["gh", "repo", "edit", args.repo, "--description", args.description]
    subprocess.run(cmd, check=True)

    topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    if topics:
        subprocess.run(["gh", "repo", "edit", args.repo, "--add-topic", ",".join(topics)], check=True)

if __name__ == "__main__":
    main()
