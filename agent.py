import json
import traceback
import os
from datetime import datetime

import progression
import gemini_generator
import github_pusher
import telegram_bot

def main():
    print("Starting Daily AI Builder Agent (Multi-Repo Mode)...")
    
    # 1. Load config
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Critcal error reading config.json: {e}")
        return

    if config.get("paused", False):
        print("Agent is currently paused in config.json. Exiting.")
        return

    # User token is REQUIRED for the multi-repo architecture
    github_user_token = os.environ.get("PAT_TOKEN")
    if not github_user_token:
        error_msg = ("CRITICAL ERROR: PAT_TOKEN is not set in environments. "
                     "This PAT is absolutely required to create a new standalone repository.")
        print(error_msg)
        telegram_bot.send_failure_notification(config, error_msg)
        return

    # 2. Load past projects
    try:
        with open("past_projects.json", "r") as f:
            past_projects = json.load(f)
    except FileNotFoundError:
        past_projects = []
        with open("past_projects.json", "w") as f:
            json.dump(past_projects, f)

    day_number = len(past_projects) + 1
    
    try:
        # 3. Get progression info
        difficulty = progression.get_difficulty(day_number)
        progress_info = progression.get_progress_info(day_number)
        print(f"Today is Day {day_number}. Target difficulty: {difficulty}")

        # 4. Generate project
        print("Calling Gemini to generate project files...")
        project_data = gemini_generator.generate_project(
            config, day_number, difficulty, past_projects, retries=1
        )
        
        project_name = project_data["_metadata"]["project_name"]
        print(f"Generated project: {project_name}")
        
        # 5. basic validation 
        if "package.json" not in project_data and "package.json" not in [k.split("/")[-1] for k in project_data.keys()]:
            raise ValueError("Generated project is missing package.json!")
        
        # 6. Save project locally to temp folder
        repo_name, temp_base_path = github_pusher.save_project(day_number, project_name, project_data)
        
        # 7. Create GitHub Repo and Push
        print(f"Requesting GitHub to create a new repo titled '{repo_name}'...")
        github_pusher.create_github_repo(
            token=github_user_token, 
            repo_name=repo_name, 
            description=f"My daily coding practice: {project_name}"
        )
        
        # We need the user's name/email to commit as them, rather than github-actions bot
        github_username = config.get('github_username', 'Developer')
        
        repo_created_url = f"https://github.com/{github_username}/{repo_name}.git"
        github_pusher.push_to_new_repo(
            base_path=temp_base_path, 
            repo_url=repo_created_url, 
            token=github_user_token, 
            day_number=day_number, 
            project_name=project_name,
            github_username=github_username
        )

        # 8. Update past_projects.json
        stack_used = ", ".join(config.get("languages", [])) + " + " + ", ".join(config.get("styling", []))
        repo_web_url = f"https://github.com/{config.get('github_username')}/{repo_name}"

        new_project_entry = {
            "day": day_number,
            "name": project_name,
            "difficulty": progress_info["current_level"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "stack": stack_used,
            "repo_url": repo_web_url
        }
        past_projects.append(new_project_entry)
        
        with open("past_projects.json", "w") as f:
            json.dump(past_projects, f, indent=2)
            
        # 9. Update main controller README
        total_projects = len(past_projects)
        github_pusher.update_readme(
            config, 
            total_projects, 
            progress_info["current_level"], 
            streak=total_projects, # Assuming continuous streak based on len
            today_project_name=project_name, 
            repo_name=repo_name,
            progress_info=progress_info
        )
        
        # 10. Commit and Push main tracking files
        github_pusher.commit_and_push_main(day_number, project_name)
        
        # 11. Telegram Notification (now pointing to the new standalone repo)
        telegram_bot.send_build_notification(
            config, day_number, project_name, 
            progress_info["current_level"], stack_used, repo_web_url, progress_info
        )
        
        # 12. Check milestones
        # Check level up
        if day_number > 1:
            prev_level = progression.get_level_name(day_number - 1)
            curr_level = progress_info["current_level"]
            if prev_level != curr_level:
                telegram_bot.send_levelup_notification(config, curr_level)
                
        # Check streak/day milestones
        milestones = [7, 30, 60, 90, 100, 365]
        if day_number in milestones:
            telegram_bot.send_milestone_notification(config, day_number, "streak")
            
        print("Daily multi-repo build completed successfully!")
        
    except Exception as e:
        error_msg = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"Build failed!\n{error_msg}")
        # Send failure to telegram
        telegram_bot.send_failure_notification(config, str(e))

if __name__ == "__main__":
    main()
