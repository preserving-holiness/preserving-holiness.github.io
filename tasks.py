# -*- coding: utf-8 -*-

from invoke import task
from invoke.watchers import Responder
from pathlib import Path
import os
import shutil
import sys
import webbrowser
from datetime import datetime

# --- Configuration ---
CONFIG = {
    "content_path": Path("content"),
    "output_path": Path("output"),
    "deploy_path": Path("output"),
    "port": 8000,
    "pelican_binary": "pelican",
    "pelican_conf": "pelicanconf.py",
    "publish_conf": "publishconf.py",
    "article_summaries_path": Path(r"f:\Article Summaries"),
}

def get_metadata_from_user(file_content):
    """Prompt user for metadata if not found in file."""
    metadata = {}
    lines = file_content.splitlines()

    # Simple check for existing metadata block
    existing_metadata = {}
    if lines and ":" in lines[0]:
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                existing_metadata[key.strip().lower()] = value.strip()
            else:
                break

    # Title
    if "title" not in existing_metadata:
        metadata["Title"] = input("Enter Title: ")
    else:
        metadata["Title"] = existing_metadata["title"]

    # Date
    metadata["Date"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Category
    if "category" not in existing_metadata:
        metadata["Category"] = input("Enter Category: ")
    else:
        metadata["Category"] = existing_metadata["category"]

    # Tags
    if "tags" not in existing_metadata:
        metadata["Tags"] = input("Enter Tags (comma-separated): ")
    else:
        metadata["Tags"] = existing_metadata["tags"]

    # Author
    if "author" not in existing_metadata:
        metadata["Author"] = input("Enter Author: ")
    else:
        metadata["Author"] = existing_metadata["author"]

    # Summary
    if "summary" not in existing_metadata:
        summary_lines = []
        for line in lines:
            if line.startswith("##"):
                break
            if line.strip() and not line.startswith("#"):
                summary_lines.append(line.strip())
        if summary_lines:
             metadata["Summary"] = " ".join(summary_lines)[:150] # Take a portion as summary
        else:
            metadata["Summary"] = input("Enter Summary: ")
    else:
        metadata["Summary"] = existing_metadata["summary"]

    return metadata

@task
def post(c):
    """Post the next article from the summaries folder with metadata."""
    src_path = CONFIG["article_summaries_path"]
    dst_path = CONFIG["content_path"] / "posts"

    print(f"Checking for summaries in: {src_path}")
    print(f"Does the path exist? {src_path.exists()}")
    print(f"Is it a directory? {src_path.is_dir()}")

    src_files = sorted([p for p in src_path.glob("*.md") if p.name != "processed_files.log"])
    dst_files = [p.name for p in dst_path.glob("*.md")]

    print("Source files found:", [p.name for p in src_files])
    print("Destination files found:", dst_files)

    next_post_path = None
    for src_file in src_files:
        if src_file.name not in dst_files:
            next_post_path = src_file
            break

    if next_post_path:
        with open(next_post_path, "r", encoding="utf-8") as f:
            content = f.read()

        metadata = get_metadata_from_user(content)
        metadata_str = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
        
        # Remove existing h1 if present, as Title metadata will replace it
        content_lines = content.splitlines()
        if content_lines and content_lines[0].startswith("# "):
            content = "\n".join(content_lines[1:]).lstrip()

        new_content = f"{metadata_str}\n\n{content}"

        target_file = dst_path / next_post_path.name
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"--> Successfully posted '{next_post_path.name}' to {target_file}")
    else:
        print("--> No new articles to post.")

@task
def clean(c):
    """Remove generated files"""
    if os.path.isdir(CONFIG["output_path"]):
        shutil.rmtree(CONFIG["output_path"])
    if os.path.isdir(".cache"):
        shutil.rmtree(".cache")

@task
def build(c):
    """Build local version of site"""
    c.run(f"{CONFIG['pelican_binary']} {CONFIG['content_path']} -o {CONFIG['output_path']} -s {CONFIG['pelican_conf']}")

@task
def rebuild(c):
    """`clean` then `build`"""
    clean(c)
    build(c)

@task
def serve(c):
    "Build and serve the site locally for development"
    c.run("pelican -s pelicanconf.py -r")
    c.run("cd output && python -m http.server 8000 --bind 127.0.0.1")

@task
def publish(c):
    """Build production version of site"""
    c.run(f"{CONFIG['pelican_binary']} {CONFIG['content_path']} -o {CONFIG['output_path']} -s {CONFIG['publish_conf']}")

@task
def preview(c):
    "Build and serve the site locally"
    c.run("pelican -s pelicanconf.py")
    c.run("pelican -l -r -b 127.0.0.1")

@task
def deploy(c):
    "Build the site for production and push to GitHub Pages"
    c.run("pelican -s publishconf.py")
    c.run('ghp-import output -b main -m "Update site" -p -f')
    print("--> Site deployed to main branch on GitHub.")
    c.run("git add .")
    c.run('git commit -m "Update source code"')
    c.run("git push origin source")
    print("--> Source code pushed to source branch on GitHub.")

@task
def push_source(c):
    """Commit and push the source code to the 'source' branch"""
    c.run("git add .")
    responder = Responder(
        pattern=r"Enter commit message: ",
        response="Site update\n",
    )
    c.run('git commit -m "Site update"', watchers=[responder], pty=True)
    c.run("git push origin source")
    print("\n---> Your source code has been pushed to the 'source' branch!") 