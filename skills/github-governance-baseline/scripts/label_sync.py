#!/usr/bin/env python3
import argparse, json, subprocess

def label_exists(repo, name):
    proc = subprocess.run(["gh", "label", "list", "--repo", repo, "--search", name, "--limit", "200"],
                          capture_output=True, text=True, check=True)
    return any(line.split("\t", 1)[0] == name for line in proc.stdout.splitlines() if line.strip())

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--labels-file", required=True)
    args = p.parse_args()

    labels = json.load(open(args.labels_file, encoding="utf-8"))
    for label in labels:
        name = label["name"]
        color = label["color"]
        desc = label.get("description", "")
        if label_exists(args.repo, name):
            cmd = ["gh", "label", "edit", name, "--repo", args.repo, "--color", color, "--description", desc]
        else:
            cmd = ["gh", "label", "create", name, "--repo", args.repo, "--color", color, "--description", desc]
        print("$", " ".join(cmd))
        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
