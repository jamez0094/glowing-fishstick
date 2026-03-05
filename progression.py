import math

def get_difficulty(day_number):
    """
    Returns the difficulty level string based on the current day number.
    - Days 1–15:   Beginner
    - Days 16–35:  Easy
    - Days 36–60:  Intermediate
    - Days 61–90:  Hard
    - Days 91+:    Expert
    """
    if day_number <= 15:
        return "Beginner (simple static pages, basic components)"
    elif day_number <= 35:
        return "Easy (multi-component React, small interactivity)"
    elif day_number <= 60:
        return "Intermediate (React + real APIs or Node backend)"
    elif day_number <= 90:
        return "Hard (full stack, frontend + backend + database)"
    else:
        return "Expert (complex production-level applications)"

def get_level_name(day_number):
    """Returns just the concise level name without descriptions."""
    if day_number <= 15: return "Beginner"
    elif day_number <= 35: return "Easy"
    elif day_number <= 60: return "Intermediate"
    elif day_number <= 90: return "Hard"
    else: return "Expert"

def get_progress_info(day_number):
    """
    Calculates progress towards the next difficulty level.
    Returns a dictionary with level information, progress percentage, and progress bar.
    """
    level_milestones = [
        (1, 15, "Beginner", "Easy"),
        (16, 35, "Easy", "Intermediate"),
        (36, 60, "Intermediate", "Hard"),
        (61, 90, "Hard", "Expert")
    ]
    
    current_level = get_level_name(day_number)
    
    # Handle maximum level
    if day_number > 90:
        return {
            "current_level": current_level,
            "next_level": "Max Level Reached",
            "projects_to_next": 0,
            "progress_percent": 100,
            "progress_bar": "[████████████████████] 100%"
        }
        
    next_level = ""
    start_day = 1
    end_day = 15
    
    for start, end, lvl, nxt in level_milestones:
        if start <= day_number <= end:
            start_day = start
            end_day = end
            next_level = nxt
            break
            
    total_days_in_level = (end_day - start_day) + 1
    days_completed_in_level = (day_number - start_day) + 1
    projects_to_next = (end_day - day_number) + 1
    
    progress_percent = int((days_completed_in_level / total_days_in_level) * 100)
    
    # 20 block visual progress bar
    filled_blocks = math.floor((progress_percent / 100) * 20)
    empty_blocks = 20 - filled_blocks
    progress_bar = f"[{'█' * filled_blocks}{'░' * empty_blocks}] {progress_percent}%"
    
    return {
        "current_level": current_level,
        "next_level": next_level,
        "projects_to_next": projects_to_next,
        "progress_percent": progress_percent,
        "progress_bar": progress_bar
    }
