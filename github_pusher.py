import os
import subprocess

def save_project(day_number, project_name, files):
    """
    Saves the generated project files to the local file system.
    Returns the project folder name.
    """
    folder_name = f"day-{day_number:03d}-{project_name.lower().replace(' ', '-')}"
    base_path = os.path.join("projects", folder_name)
    
    os.makedirs(base_path, exist_ok=True)
    
    for relative_path, content in files.items():
        if relative_path == "_metadata":
            continue
            
        file_path = os.path.join(base_path, relative_path)
        
        # Ensure subdirectories exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    print(f"Saved project files to {base_path}/")
    return folder_name

def update_readme(config, total_projects, difficulty_level, streak, today_project_name, progress_info):
    """
    Updates the main dashboard README.md for the repository.
    """
    readme_template = f"""# 🤖 AI Builder Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Total Projects Built:  {total_projects}
🎯 Current Level:         {difficulty_level}
🔥 Day Streak:            {streak} days
📅 Today's Build:         {today_project_name}
⏭️  Next Level in:         {progress_info['projects_to_next']} projects
━━━━━━━━━━━━━━━━━━━━━━━━━━

Progress to {progress_info['next_level']}:
{progress_info['progress_bar']}

## About
This repository is fully autonomous. Every day at 9am UTC, an AI agent wakes up via GitHub Actions, uses the Gemini API to write a brand new coding project based on my current progression level, and pushes it here. 
You can find the scripts that power this automation in the root directory.

## Stack Tracker ⚡
Currently building projects using: {', '.join(config.get('languages', []))} and {', '.join(config.get('styling', []))}.
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_template)
    print("Updated main dashboard README.md")

def run_cmd(cmd):
    """Helper to run a shell command and print output/errors"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(result.stderr)
        raise Exception(f"Git command failed: {cmd}")
    return result.stdout

def commit_and_push(day_number, project_name):
    """
    Stages, commits, and pushes changes to GitHub.
    """
    try:
        print("Staging files...")
        run_cmd("git add .")
        
        # Check if there are changes to commit
        status = run_cmd("git status --porcelain")
        if not status.strip():
            print("No changes to commit.")
            return

        print("Committing files...")
        commit_msg = f"feat(day-{day_number}): Generated {project_name}"
        run_cmd(f'git commit -m "{commit_msg}"')
        
        print("Pushing to GitHub...")
        run_cmd("git push origin main")
        print("Successfully pushed to GitHub!")
    except Exception as e:
        print(f"Failed to commit and push: {e}")
        # Re-raise to be caught by the main agent for sending Telegram notification
        raise
