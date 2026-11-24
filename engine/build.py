"""Render a day's batch.

usage: python3 engine/build.py posts/YYYY-MM-DD/batch.json

Writes PNGs next to batch.json and a manifest.json listing every file per post.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import render_post, story_frame  # noqa: E402


def main(path):
    with open(path) as f:
        batch = json.load(f)
    outdir = os.path.dirname(os.path.abspath(path))
    manifest = {}
    for p in batch["posts"]:
        files = render_post(p, outdir)
        manifest[p["id"]] = [os.path.basename(x) for x in files]
        if p.get("story"):
            sp = os.path.join(outdir, f"{p['id']}_story.png")
            story_frame(files[0], sp)
            manifest[p["id"] + "_story"] = [os.path.basename(sp)]
        print(p["id"], "->", ", ".join(manifest[p["id"]]))
    with open(os.path.join(outdir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)


if __name__ == "__main__":
    main(sys.argv[1])
