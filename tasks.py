# -*- coding: utf-8 -*-

from invoke import task
from invoke.watchers import Responder
from pathlib import Path
import os
import shutil
import sys
import webbrowser

# --- Configuration ---
CONFIG = {
    "content_path": Path("content"),
    "output_path": Path("output"),
    "deploy_path": Path("output"),
    "port": 8000,
    "pelican_binary": "pelican",
    "pelican_conf": "pelicanconf.py",
    "publish_conf": "publishconf.py",
}

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