import progression

days_to_test = [1, 15, 16, 35, 36, 60, 61, 90, 91]

print("Day | Difficulty | Level | Next Level | To Next | % | Bar")
print("-" * 75)
for day in days_to_test:
    diff = progression.get_difficulty(day)
    lvl = progression.get_level_name(day)
    info = progression.get_progress_info(day)
    
    diff_short = diff.split(" ")[0]
    
    print(f"{day:3d} | {diff_short:10s} | {info['current_level']:10s} | {info['next_level']:15s} | {info['projects_to_next']:5d} | {info['progress_percent']:3d} | {info['progress_bar']}")

