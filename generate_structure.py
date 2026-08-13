import os
from pathlib import Path

# Define the folder and file structure
STRUCTURE = {
    "database": [
        "tournament.db"
    ],
    "models": [
        "tournament.py",
        "team.py",
        "player.py",
        "match.py"
    ],
    "routes": [
        "home.py",
        "tournament.py",
        "teams.py",
        "swiss.py"
    ],
    "services": [
        "swiss_engine.py",
        "leaderboard.py",
        "pairing.py"
    ],
    "static/css": [
        "style.css"
    ],
    "static/js": [
        "app.js"
    ],
    "static/images": [], # Empty directory
    "templates": [
        "base.html",
        "index.html",
        "setup.html",
        "teams.html",
        "leaderboard.html",
        "round.html",
        "match.html"
    ],
    "utils": [
        "helpers.py"
    ],
    "": [ # Root level files
        "app.py",
        "config.py",
        "requirements.txt"
    ]
}

def create_structure(base_dir="chess tournament"):
    base_path = Path(base_dir)
    
    print(f"Creating project structure in: {base_path.resolve()}\n")
    
    # Track created items for a nice summary
    dirs_created = 0
    files_created = 0

    for folder, files in STRUCTURE.items():
        # Define the target directory path
        target_dir = base_path / folder if folder else base_path
        
        # Create directory if it doesn't exist
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
            dirs_created += 1
            print(f"[DIR]  Created: {target_dir}")
            
        # Create the files inside the directory
        for file in files:
            file_path = target_dir / file
            if not file_path.exists():
                file_path.touch()
                files_created += 1
                print(f"[FILE] Created: {file_path}")
            else:
                print(f"[INFO] Already exists: {file_path}")

    print("\n" + "="*40)
    print(f"Success! Created {dirs_created} directories and {files_created} files.")
    print("="*40)

if __name__ == "__main__":
    create_structure()