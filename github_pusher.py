import os
import json
import requests
import subprocess
import shutil

def save_project(day_number, project_name, files):
    """
    Saves the generated project files to a temporary local folder for pushing.
    """
    folder_name = f"day-{day_number:03d}-{project_name.lower().replace(' ', '-')}"
    base_path = os.path.join("temp_projects", folder_name)
    
    # Clean up previous temp builds if they exist
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
        
    os.makedirs(base_path, exist_ok=True)
    
    for relative_path, content in files.items():
        if relative_path == "_metadata":
            continue
            
        file_path = os.path.join(base_path, relative_path)
        
        # Ensure subdirectories exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    print(f"Saved project files to temporary {base_path}/")
    return folder_name, base_path

def create_github_repo(token, repo_name, description=""):
    """
    Uses the GitHub API to create a new public repository for the user.
    """
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "description": description,
        "private": False, # Always public to show off!
        "auto_init": False # We will push our own initial commit
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"Successfully created GitHub repository: {repo_name}")
        return response.json()["clone_url"]
    elif response.status_code == 422 and "name already exists on this account" in response.text:
         # Repo already exists, fetch it to continue
         print(f"Repository {repo_name} already exists. Fetching URL instead.")
         user_resp = requests.get("https://api.github.com/user", headers=headers)
         username = user_resp.json()["login"]
         return f"https://github.com/{username}/{repo_name}.git"
    else:
        raise Exception(f"Failed to create repository. Status {response.status_code}: {response.text}")

def run_cmd(cmd, cwd=None):
    """Helper to run a shell command and print output/errors"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Command failed: {cmd} in {cwd}")
        print(result.stderr)
        raise Exception(f"Git command failed: {cmd}")
    return result.stdout

def push_to_new_repo(base_path, repo_url, token, day_number, project_name):
    """
    Initializes a git repository in the *temporary folder*, configures auth, and pushes to the new remote.
    """
    # Insert token into the remote URL to allow pushing via HTTPS
    auth_url = repo_url.replace("https://", f"https://x-access-token:{token}@")
    
    print(f"Pushing project to standalone repository {repo_url}...")
    
    run_cmd("git init -b main", cwd=base_path)
    run_cmd("git config user.name 'github-actions[bot]'", cwd=base_path)
    run_cmd("git config user.email 'github-actions[bot]@users.noreply.github.com'", cwd=base_path)
    
    run_cmd("git add .", cwd=base_path)
    commit_msg = f"feat(day-{day_number}): Generated {project_name}"
    run_cmd(f'git commit -m "{commit_msg}"', cwd=base_path)
    
    run_cmd(f"git remote add origin {auth_url}", cwd=base_path)
    
    # Try to push. If the repo was pre-existing and isn't empty, this might fail,
    # but for a daily AI challenge we assume the repo is new and empty.
    run_cmd("git push -uf origin main", cwd=base_path)
    print("Successfully pushed to daily standalone repository!")

def update_readme(config, total_projects, difficulty_level, streak, today_project_name, repo_name, progress_info):
    """
    Updates the main dashboard README.md for the controller repository.
    """
    readme_template = f"""# 🤖 AI Builder Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Total Projects Built:  {total_projects}
🎯 Current Level:         {difficulty_level}
🔥 Day Streak:            {streak} days
📅 Today's Build:         [{today_project_name}](https://github.com/{config.get('github_username')}/{repo_name})
⏭️  Next Level in:         {progress_info['projects_to_next']} projects
━━━━━━━━━━━━━━━━━━━━━━━━━━

Progress to {progress_info['next_level']}:
{progress_info['progress_bar']}

## About
This repository is fully autonomous. Every day at 9am UTC, an AI agent wakes up via GitHub Actions, uses the Gemini API to write a brand new coding project based on my current progression level, creates a brand new repository for it, and pushes it there. 
You can find the scripts that power this automation in the root directory.

## Stack Tracker ⚡
Currently building projects using: {', '.join(config.get('languages', []))} and {', '.join(config.get('styling', []))}.
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_template)
    print("Updated main dashboard README.md")

def commit_and_push_main(day_number, project_name):
    """
    Stages, commits, and pushes changes tracking files (README, past_projects.json) to the central controller GitHub repo.
    """
    try:
        print("Staging config/tracking files in main repo...")
        # Only add the tracking files, NOT the temp_projects directory
        run_cmd("git add README.md past_projects.json")
        
        status = run_cmd("git status --porcelain")
        if not status.strip():
            print("No tracking changes to commit.")
            return

        print("Committing tracking files...")
        commit_msg = f"chore(tracker): Log completion of Day {day_number} - {project_name}"
        run_cmd(f'git commit -m "{commit_msg}"')
        
        print("Pushing tracking updates to main GitHub...")
        run_cmd("git push origin main")
        print("Successfully synced orchestrator repository!")
    except Exception as e:
        print(f"Failed to commit and push main tracker: {e}")
        raise
