from diagnostic.verify import (
    VerificationStatus,
    is_ffmpeg_installed,
    verify_ffmpeg_installed,
    verify_using_linux,
    verify_internet_connection,
    verify_python_installed
)
from pathlib import Path
import subprocess
import logging

MODULE_NAME: str = "SetupCamera"

logger = logging.getLogger('Default')


"""
Section: APT-GET repository updated
"""

VS_APTGET_UPDATED = VerificationStatus.NotChecked


def verify_aptget_updated() -> bool:
    global VS_APTGET_UPDATED

    if VS_APTGET_UPDATED == VerificationStatus.Verified:
        return True
    if VS_APTGET_UPDATED == VerificationStatus.Failed:
        return False

    try:
        result = subprocess.run(['sudo', 'apt-get', 'update'], capture_output=True, text=True)
        result.check_returncode()
        logger.info('Updated apt-get repository.')
        VS_APTGET_UPDATED = VerificationStatus.Verified
        return True
    except Exception:
        VS_APTGET_UPDATED = VerificationStatus.Failed
        logger.error('Could not update apt-get repository.')
        return False


"""
Section: Install ffmpeg
"""


def install_ffmpeg() -> bool:
    if is_ffmpeg_installed():
        verify_ffmpeg_installed()

    # Is user running linux?
    if not verify_using_linux():
        logger.error('Linux OS is required for FFmpeg installation.')
        return False

    # Does user have an internet connection?
    if not verify_internet_connection():
        logger.error('Internet is required for FFmpeg installation.')
        return False

    # Update apt-get repository
    if not verify_aptget_updated():
        logger.error('Updated apt-get repository required for FFmpeg installation.')
        return False

    # Install ffmpeg
    try:
        result = subprocess.run(['sudo', 'apt-get', 'install', 'ffmpeg', '-y'], capture_output=True)
        result.check_returncode()
    except Exception:
        logger.error('FFmpeg could not be installed.')
        return False

    # Check installation succeeded
    if not verify_ffmpeg_installed():
        logger.error('FFmpeg could not be installed.')
        return False

    logger.info('FFmpeg successfully installed.')
    return True


"""
Section: Install Mediamtx
"""

VS_MEDIAMTX_INSTALLED = VerificationStatus.NotChecked


def is_mediamtx_installed(mediamtx_path: Path) -> bool:
    required_files = {'LICENSE', 'mediamtx', 'mediamtx.yml'}

    for file in mediamtx_path.glob('*'):
        if file.name in required_files and file.is_file():
            required_files.remove(file.name)

    return len(required_files) == 0


def verify_mediamtx_installed(mediamtx_path: Path) -> bool:
    global VS_MEDIAMTX_INSTALLED

    if VS_MEDIAMTX_INSTALLED == VerificationStatus.Verified:
        return True
    if VS_MEDIAMTX_INSTALLED == VerificationStatus.Failed:
        return False

    if not is_mediamtx_installed(mediamtx_path):
        VS_MEDIAMTX_INSTALLED = VerificationStatus.Failed
        logger.error('Mediamtx not installed.')
        return False

    VS_MEDIAMTX_INSTALLED = VerificationStatus.Verified
    logger.info('Mediamtx installation verified.')
    return True


def install_mediamtx(mediamtx_path: Path,
                     version: str = '1.11.3') -> bool:
    if is_mediamtx_installed(mediamtx_path):
        verify_mediamtx_installed(mediamtx_path)

    if not mediamtx_path.exists():
        mediamtx_path.mkdir(exist_ok=True, parents=True)
    if not mediamtx_path.is_dir():
        logger.error(f'Provided path is not a directory: {mediamtx_path}')
        return False

    def construct_tar_filename() -> str:
        return f'mediamtx_v{version}_linux_amd64.tar.gz'

    def construct_release_link() -> str:
        return 'https://github.com/bluenviron/mediamtx/releases/download/' \
               f'v{version}/{construct_tar_filename()}'

    # Retrieve the release from github
    try:
        result = subprocess.run(['wget', construct_release_link()],
                                capture_output=True, text=True)
        result.check_returncode()
    except Exception:
        logger.error('Could not retrieve mediamtx release from github.')
        return False

    # Extract the file contents and then remove the tar file
    try:
        result = subprocess.run(['tar', '-xf', construct_tar_filename(), '-C', str(mediamtx_path)],
                                capture_output=True, text=True)
        result.check_returncode()
        subprocess.run(['rm', construct_tar_filename()])
    except Exception:
        logger.error(f'Could not extract tar file {construct_tar_filename()}')
        return False

    # Update configuration
    try:
        config_path = mediamtx_path / 'mediamtx.yml'
        with open(config_path, 'w') as config_file:
            config_file.write("paths:\n\tall:\n\t\tsource: publisher\n")
    except Exception:
        logger.error('Could not update configuration file mediamtx.yaml.')
        return False

    # Check installation succeeded
    if not verify_mediamtx_installed(mediamtx_path):
        logger.error('Mediamtx could not be installed.')
        return False

    logger.info('Mediamtx successfully installed.')
    return True


if __name__ == "__main__":
    if not verify_python_installed():
        logger.error('Python required.')
        exit(1)

    if not verify_using_linux():
        logger.error('Linux OS required.')
        exit(1)

    # FFmpeg
    if not is_ffmpeg_installed():
        selection = input('Install FFmpeg? (Y|N): ')
        if selection.lower() in ['y', 'yes']:
            install_ffmpeg()

    # MediaMTX
    selection = input('Install MediaMTX? (Y|N): ')
    if selection.lower() in ['y', 'yes']:
        mediamtx_path = Path(input('Where would you like to install MediaMTX: '))
        install_mediamtx(mediamtx_path)
