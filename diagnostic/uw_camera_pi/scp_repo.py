from pathlib import Path
import subprocess
import os

PROJECT_DIR = Path(__file__).parent.parent.parent.absolute()

USERNAME = 'underwater'
HOSTNAME = 'uw-camera'

command = ['rsync', '-rav']
command.append('--exclude=.git')  # Can't add this to .gitignore

GITIGNORE_PATH = PROJECT_DIR/'.gitignore'
with open(GITIGNORE_PATH, 'r') as gitignore_file:
    for exclusion in gitignore_file.readlines():
        command.append(f'--exclude={exclusion.strip()}')

os.chdir(PROJECT_DIR.parent)
command += ['MATE-2024', f'{USERNAME}@{HOSTNAME}:/home/{USERNAME}']

subprocess.run(command)
