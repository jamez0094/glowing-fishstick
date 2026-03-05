import json
import traceback
from datetime import datetime

import progression
import gemini_generator
import github_pusher
import telegram_bot

def main():
    print("Starting Daily AI Builder Agent...")
    
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
        
        # 6. Save project locally
        folder_name = github_pusher.save_project(day_number, project_name, project_data)
        
        # 7. Update past_projects.json
        stack_used = ", ".join(config.get("languages", [])) + " + " + ", ".join(config.get("styling", []))
        
        new_project_entry = {
            "day": day_number,
            "name": project_name,
            "difficulty": progress_info["current_level"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "stack": stack_used
        }
        past_projects.append(new_project_entry)
        
        with open("past_projects.json", "w") as f:
            json.dump(past_projects, f, indent=2)
            
        # 8. Update README
        total_projects = len(past_projects)
        github_pusher.update_readme(
            config, 
            total_projects, 
            progress_info["current_level"], 
            streak=total_projects, # Assuming continuous streak based on len
            today_project_name=project_name, 
            progress_info=progress_info
        )
        
        # 9. Commit and Push
        github_pusher.commit_and_push(day_number, project_name)
        
        # 10. Telegram Notification
        telegram_bot.send_build_notification(
            config, day_number, project_name, 
            progress_info["current_level"], stack_used, progress_info
        )
        
        # 11. Check milestones
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
            
        print("Daily build completed successfully!")
        
    except Exception as e:
        error_msg = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"Build failed!\n{error_msg}")
        # Send failure to telegram
        telegram_bot.send_failure_notification(config, str(e))

if __name__ == "__main__":
    main()
