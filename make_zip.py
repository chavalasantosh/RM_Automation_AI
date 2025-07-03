import os
import shutil

# Name of the backup zip file
backup_name = 'RME_Cursor_backup'
backup_zip = backup_name + '.zip'

# Exclude the backup zip itself if it exists
exclude = {backup_zip}

# Get all files and directories in the current directory
items = [item for item in os.listdir('.') if item not in exclude]

# Create the zip archive
shutil.make_archive(backup_name, 'zip', '.', None)

print(f'Backup created: {backup_zip}') 