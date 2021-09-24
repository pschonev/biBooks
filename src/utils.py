from pathlib import Path

def create_folder(folder):
    path = Path(folder)
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(f"Folder is already there - {folder}")
    else:
        print(f"Folder was created at {folder}")