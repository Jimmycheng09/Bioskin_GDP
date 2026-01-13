from github import Github
import json
import random
from datetime import datetime
import pytz # For nice timezone handling

# --- 1. CONFIGURATION (EDIT THESE) ---
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN_HERE"      # Paste your Personal Access Token
REPO_NAME = "your-username/your-repo-name"   # e.g. "johndoe/sensor-project"
FILE_PATH = "sensor_data.json"               # The file must exist on GitHub (even if just [])

def update_github_json():
    print("Connecting to GitHub...")
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    try:
        # --- 2. FETCH EXISTING DATA ---
        # We need the current file content AND its 'sha' (ID) to update it
        contents = repo.get_contents(FILE_PATH)
        raw_data = contents.decoded_content.decode()
        
        if not raw_data:
            data = [] # Handle empty file
        else:
            data = json.loads(raw_data)
            
        # --- 3. GENERATE RANDOM DATA (5 SENSORS) ---
        # Singapore Timezone (Asia/Singapore)
        tz = pytz.timezone('Asia/Singapore')
        
        new_entry = {
            "date": datetime.now(tz).strftime('%Y-%m-%d'),
            "time": datetime.now(tz).strftime('%H:%M:%S'),
            "sensor1": random.randint(20, 30),  # Random Temp ~25C
            "sensor2": random.randint(20, 30),
            "sensor3": random.randint(20, 30),
            "sensor4": random.randint(0, 50),   # Random Pressure
            "sensor5": random.randint(0, 50)
        }
        
        # --- 4. APPEND AND PUSH ---
        data.append(new_entry)
        print(f"Adding new row: {new_entry}")
        
        # The 'sha' tells GitHub exactly which version of the file we are replacing
        repo.update_file(
            path=FILE_PATH,
            message=f"Test data update: {new_entry['time']}",
            content=json.dumps(data, indent=2), # Pretty print JSON
            sha=contents.sha
        )
        
        print("✅ Success! File updated on GitHub.")

    except Exception as e:
        print(f"❌ Error: {e}")

# Run the function
if __name__ == "__main__":
    # You can put this in a while True loop if you want continuous testing
    update_github_json()
