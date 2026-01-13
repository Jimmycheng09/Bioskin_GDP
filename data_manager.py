from github import Github
import json
from datetime import datetime
import pytz # For timezone handling

# --- CONFIGURATION ---
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN_HERE"
REPO_NAME = "your-username/your-repo-name" # e.g., "johndoe/sensor-project"
MAIN_FILE_PATH = "sensor_data.json" # The file the ESP32 writes to

def check_and_archive_data():
    # 1. Connect to GitHub
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    try:
        # 2. Fetch the current 'sensor_data.json'
        contents = repo.get_contents(MAIN_FILE_PATH)
        raw_data = contents.decoded_content.decode()
        
        # If file is empty, stop
        if not raw_data:
            print("File is empty. No archiving needed.")
            return

        json_data = json.loads(raw_data)
        
        if not json_data:
            print("JSON list is empty. No archiving needed.")
            return

        # 3. Check the Date of the data
        # We look at the first entry to see what date this data belongs to.
        # Assuming your JSON looks like: [{"date": "2023-10-25", "value": ...}, ...]
        first_entry_date = json_data[0].get('date') # Adjust key if yours is different (e.g., 'Date')
        
        # Get Today's Date
        tz = pytz.timezone('Asia/Singapore')
        today_date = datetime.now(tz).strftime('%Y-%m-%d')
        
        # 4. LOGIC: If data is NOT from today, Archive it!
        if first_entry_date != today_date:
            print(f"Old data found ({first_entry_date}). Archiving...")
            
            # A. Create the Archive File Name (e.g., "Data_2023-10-25.json")
            archive_filename = f"Data_{first_entry_date}.json"
            
            # B. Create the new file on GitHub
            try:
                repo.create_file(
                    path=f"archive/{archive_filename}", # Put in an 'archive' folder
                    message=f"Archiving data from {first_entry_date}",
                    content=raw_data
                )
                print(f"Created {archive_filename}")
            except Exception as e:
                print(f"File already exists or error: {e}")
                return

            # C. Clean the Main File (Reset to empty list [])
            repo.update_file(
                path=MAIN_FILE_PATH,
                message="Resetting main file for new data",
                content="[]", # Empty JSON list
                sha=contents.sha
            )
            print("Main file cleaned successfully.")
            
        else:
            print("Data is from today. No action needed.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the check
if __name__ == "__main__":
    check_and_archive_data()
