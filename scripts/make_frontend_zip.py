import os
import zipfile
from pathlib import Path
import shutil

def create_frontend_zip():
    # Define the directories to include
    frontend_dirs = [
        'static',
        'templates'
    ]
    
    # Define the output zip file name
    zip_filename = 'frontendrme.zip'
    
    # Create a temporary directory to organize files
    temp_dir = Path('temp_frontend')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Copy frontend directories to temp directory
    for dir_name in frontend_dirs:
        src_dir = Path(dir_name)
        if src_dir.exists():
            dst_dir = temp_dir / dir_name
            shutil.copytree(src_dir, dst_dir)
    
    # Create zip file
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(temp_dir)
                zipf.write(file_path, arcname)
    
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    
    print(f"Created {zip_filename} with frontend files")
    print("\nIncluded directories:")
    for dir_name in frontend_dirs:
        print(f"- {dir_name}/")

if __name__ == '__main__':
    create_frontend_zip() 