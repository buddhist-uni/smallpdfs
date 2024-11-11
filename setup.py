#!/bin/python3

import subprocess
from pathlib import Path
import re

README_TEMPLATE = """# {repo}

This is a simple collection of mostly
[Creative Commons Non-Commercial (No Derivatives) Licence](https://creativecommons.org/licenses/by-nc-nd/4.0/)d
content used by the [Open Buddhist University](https://www.buddhistuniversity.net/).

For more information about an item's source,
[look up its entry on the website](https://www.buddhistuniversity.net/search/)
or cross reference these files against [our BibTex database](https://buddhistuniversity.net/content.bib).
"""

HOMEPAGE_TEMPLAGE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{repo} @ The Open Buddhist University</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css">
  </head>
  <body>
    <div class="container">
      <h1 class="title">The {repo} Content Bucket</h1>
      <h2 class="subtitle">@ The Open Buddhist University</h2>
      <p>
        <a href="https://github.com/{username}/{repo}">https://github.com/{username}/{repo}</a>
      </p>
    </div>
  </body>
</html>
"""

ZENODO_TEMPLATE = """{
  "title": "The Open Buddhist University {repo}",
  "keywords": ["buddhism"],
  "upload_type": "lesson",
  "description": "<p>A collection of free-distribution files for teaching Buddhism and related topics.</p>",
  "creators": [{
    "name": "Khemarato Bhikkhu",
    "orcid": "0000-0003-4738-7882"
  }],
  "access_right": "open",
  "license": "cc-by-nc-4.0",
  "related_identifiers": [
    {
      "relation": "isPartOf",
      "identifier": "https://www.buddhistuniversity.net"
    },{
      "relation": "isPreviousVersionOf",
      "identifier": "https://github.com/{username}/{repo}"
    },{
      "relation": "isRequiredBy",
      "identifier": "https://doi.org/10.5281/zenodo.4448510"
    }
  ],
  "subjects": [{
    "term": "Buddhism",
    "identifier": "https://id.loc.gov/authorities/subjects/sh85017454.html",
    "scheme": "url"
  }],
  "language": "eng"
}
"""

def get_repo_name() -> tuple[str, str]:
  """Returns the GitHub username and repository name from the current git repository."""
  try:
    result = subprocess.run(['git', 'remote', '-v'], 
                capture_output=True, 
                text=True, 
                check=True)
    remote_url = result.stdout.split('\n')[0]
    
    # Define patterns for different GitHub URL formats
    # Handles both HTTPS and SSH URLs:
    # https://github.com/username/repo.git
    # git@github.com:username/repo.git
    patterns = [
      r'github\.com[:/]([^/]+)/([^/\.]+)(?:\.git)?',
      r'github\.com/([^/]+)/([^/\.]+)(?:\.git)?'
    ]
    
    for pattern in patterns:
      match = re.search(pattern, remote_url)
      if match:
        username = match.group(1)
        repo = match.group(2)
        return username, repo
        
    raise ValueError("Could not parse GitHub URL from git remote output")
    
  except subprocess.CalledProcessError as e:
    raise Exception("git command failed with error code: " + str(e.returncode) + "\n---\n" + e.stderr + "\n---\n\n(Not a git repository?)")

if __name__ == "__main__":
  username, repo = get_repo_name()
  print(f"GitHub Username: {username}")
  print(f"Repository Name: {repo}")
  print("Writing files...")
  Path(".nojekyll").touch()
  Path("index.html").write_text(HOMEPAGE_TEMPLAGE.format(repo=repo, username=username))
  Path("README.md").write_text(README_TEMPLATE.format(repo=repo))
  Path(".zenodo.json").write_text(ZENODO_TEMPLATE.format(repo=repo, username=username))
  Path("CNAME").write_text("buddhistuniversity.net/{repo}".format(repo=repo))
  print("Committing files to GitHub...")
  subprocess.run(["git", "add", "."], check=True)
  subprocess.run(["git", "commit", "-m", "Initial (automated) commit"], check=True)
  subprocess.run(["git", "push", "origin", "main"], check=True)
  print("Setting up GitHub Pages...")
  subprocess.run(["gh", "api", "-X", "PUT", "/repos/{username}/{repo}/pages", "-f", "source=main"], check=True)
  print("Done! You can rm this setup file now :)")
