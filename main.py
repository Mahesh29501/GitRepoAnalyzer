import os
import tempfile
from repo_reader import clone_git_repo

def GetGitRepo():
    repo_url = input("Enter the Github Url of the Repo: ")
    repo_name = repo_url.split("/")[-1]
    print("Cloning the repo.........")
    with tempfile.TemporaryDirectory() as local_path:
        clone_git_repo(repo_url,local_path)


GetGitRepo()