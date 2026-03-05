import os
import json
import time
import google.generativeai as genai

def get_api_key(config):
    # Prefer environment variable over config file to support GitHub Secrets
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key:
        return env_key
    return config.get("gemini_api_key")

def generate_project(config, day_number, difficulty, past_projects, retries=1):
    api_key = get_api_key(config)
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY environment variable or update config.json.")

    genai.configure(api_key=api_key)

    # Use gemini-1.5-pro or gemini-2.0-flash, specifying json format
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})

    stack = ", ".join(config.get("languages", [])) + " and " + ", ".join(config.get("styling", []))
    types = ", ".join(config.get("project_types", []))
    
    past_names = [p.get("name") for p in past_projects]
    past_names_str = ", ".join(past_names) if past_names else "None"

    prompt = f"""
    You are an expert autonomous AI developer. Your task is to generate a completely new coding project.
    
    Today is Day {day_number}.
    Difficulty level to target: {difficulty}
    Tech Stack to use: {stack}
    Acceptable project types: {types}
    
    CRITICAL RULE: NEVER REPEAT A PREVIOUS PROJECT. 
    Here are the names of projects that have already been built (DO NOT BUILD THESE):
    {past_names_str}
    
    Generate the files for this project. The project should be functional and well-documented.
    For React projects, include at least:
    - README.md (Write a professional README as if you are a human developer. DO NOT mention AI, robots, Gemini, or being generated. Do NOT mention Day numbers or the difficulty level. Just explain what the project is, its features, and how to run it.)
    - src/App.jsx
    - src/index.js (or main.jsx)
    - package.json (must have all dependencies and valid scripts like "start" and "build")
    - (Optionally) backend server files if difficulty warrants it.
    
    You must return a valid JSON object where keys are the file paths relative to the project root, and values are the string content of that file.
    Also include a special key "_metadata" with a sub-object containing "project_name" as a short string.
    
    Example response structure:
    {{
       "_metadata": {{"project_name": "Task Manager"}},
       "README.md": "# Task Manager\\n...",
       "package.json": "{{\\"name\\": \\"task-manager\\", ...}}",
       "src/App.jsx": "import React from 'react';..."
    }}
    
    The JSON must be valid, do not embed markdown code blocks around it (like ```json ... ```), just raw JSON.
    """

    for attempt in range(retries + 1):
        try:
            print(f"Calling Gemini API (Attempt {attempt + 1})...")
            response = model.generate_content(prompt)
            
            # The prompt requested JSON. Try parsing it.
            text = response.text.strip()
            # If wrapped in ```json, remove it
            if text.startswith("```json"):
                text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
            
            project_data = json.loads(text)
            
            if "_metadata" not in project_data or "project_name" not in project_data["_metadata"]:
                raise ValueError("Response missing _metadata or project_name")
            
            return project_data
            
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            if attempt < retries:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise Exception(f"Failed to generate project with Gemini after {retries + 1} attempts: {e}")
