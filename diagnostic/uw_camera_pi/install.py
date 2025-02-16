from pathlib import Path
import subprocess
import logging
import os

logger = logging.getLogger('uw-camera')
PROJECT_DIR = Path(__file__).parent.parent.parent.absolute()


def ask_if_yes(prompt: str) -> bool:
    choice = input(prompt)
    return choice.lower() in ['y', 'yes']


"""
FFmpeg
"""


def install_ffmpeg():
    if not ask_if_yes('Install FFmpeg (y|n): '):
        logger.debug('Skipping FFmpeg installation.')
        return

    try:
        subprocess.run('sudo apt-get update && sudo apt-get install ffmpeg',
                       shell=True).check_returncode()
        logger.info('Installed FFmpeg.')
    except Exception as e:
        logger.error('Failed to install FFMPEG:\n', e)


"""
MediaMTX
"""

MEDIAMTX_VERSION = "1.11.3"
MEDIAMTX_SYSTEM = "linux_arm64v8"
MEDIAMTX_RELEASE_URL = "https://github.com/bluenviron/mediamtx/releases/download"


def install_mediamtx():
    if not ask_if_yes('Install MediaMTX (y|n): '):
        logger.debug('Skipping MediaMTX installation.')
        return

    tar_filename = f'mediamtx_v{MEDIAMTX_VERSION}_{MEDIAMTX_SYSTEM}.tar.gz'
    url = f'{MEDIAMTX_RELEASE_URL}/v{MEDIAMTX_VERSION}/{tar_filename}'

    os.chdir(Path.home())

    # Download release
    try:
        subprocess.run(['wget', url]).check_returncode()
    except Exception as e:
        logger.error('Could not retreive mediamtx release:\n', e)
        os.chdir(PROJECT_DIR)
        return

    # Extract .tar.gz file
    try:
        mmtx_path = Path.home() / 'mediamtx'
        mmtx_path.mkdir(exist_ok=True)
        subprocess.run(['tar', '-xf', tar_filename, '-C', 'mediamtx']).check_returncode()
        subprocess.run(['rm', tar_filename]).check_returncode()
    except Exception as e:
        logger.error('Could not extract mediamtx:\n', e)
        os.chdir(PROJECT_DIR)
        return

    # Setup configuration
    try:
        os.chdir(mmtx_path)
        with open(mmtx_path/'mediamtx.yml', 'w') as config_file:
            config_file.writelines([
                'paths:\n',
                '  all:\n',
                '    source: publisher\n'
            ])
    except Exception as e:
        logger.error('Could not setup configurations for mediamtx:\n', e)
        os.chdir(PROJECT_DIR)
        return

    os.chdir(PROJECT_DIR)
    logger.info('Mediamtx was successfully installed.')


"""
Virtual environment
"""


def install_venv():
    if not ask_if_yes('Setup virtual environment (y|n): '):
        logger.debug('Skipping virtual environment setup.')
        return

    try:
        subprocess.run(['python', '-m', 'venv', '.env']).check_returncode()
    except Exception as e:
        logger.error('Could not create virtual environment:\n', e)
        return

    try:
        subprocess.run(['.env/bin/pip', 'install', '-r', 'requirements.txt']
                       ).check_returncode()
    except Exception as e:
        logger.error('Could not install requirements:\n', e)
        return

    logger.info('Successfully setup virtual environment:\n')


if __name__ == "__main__":
    os.chdir(PROJECT_DIR)
    install_ffmpeg()
    install_mediamtx()
    install_venv()
