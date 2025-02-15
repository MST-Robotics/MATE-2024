from enum import Enum
import subprocess
import logging
import sys
import os

logger = logging.getLogger('Default')


class VerificationStatus(Enum):
    NotChecked = 0
    Verified = 1
    Failed = 2


"""
Section: Linux OS
"""

VS_USING_LINUX = VerificationStatus.NotChecked


def is_using_linux() -> bool:
    return 'linux' in sys.platform


def verify_using_linux() -> bool:
    global VS_USING_LINUX

    if VS_USING_LINUX == VerificationStatus.Verified:
        return True
    if VS_USING_LINUX == VerificationStatus.Failed:
        return False

    if is_using_linux():
        VS_USING_LINUX = VerificationStatus.Verified
        logger.info('Linux OS verified.')
        return True
    else:
        VS_USING_LINUX = VerificationStatus.Failed
        logger.error(f'OS is not linux but {sys.platform}')
        return False


"""
Section: Internet connection
"""

VS_INTERNET_CONNECTION = VerificationStatus.NotChecked


def verify_internet_connection(test_host: str = '8.8.8.8',
                               attempts: int = 4,
                               timeout_seconds: int = 3) -> bool:
    global VS_INTERNET_CONNECTION

    if VS_INTERNET_CONNECTION == VerificationStatus.Verified:
        return True
    if VS_INTERNET_CONNECTION == VerificationStatus.Failed:
        return False

    response = os.system(
        f'ping {test_host} -c {attempts} -t {timeout_seconds} > /dev/null 2>&1')
    success = response == 0
    if success:
        logger.info('Internet connection verified.')
        VS_INTERNET_CONNECTION = VerificationStatus.Verified
        return True
    else:
        logger.error('No internet connection identified.')
        VS_INTERNET_CONNECTION = VerificationStatus.Failed
        return True


"""
Section: Python installed
"""

VS_PYTHON_VERSION = VerificationStatus.NotChecked


def verify_python_installed(minimum_version: int = 7) -> bool:
    global VS_PYTHON_VERSION

    if VS_PYTHON_VERSION == VerificationStatus.Verified:
        return True
    if VS_PYTHON_VERSION == VerificationStatus.Failed:
        return False

    # Run python3 --version
    try:
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
    except Exception:
        VS_PYTHON_VERSION = VerificationStatus.Failed
        logger.error('Python 3 not found on device.')
        return False

    # Parse python version
    try:
        py3_version = int(result.stdout.strip().split()[-1].split('.')[1])
    except Exception:
        VS_PYTHON_VERSION = VerificationStatus.Failed
        logger.error(f'Python version could not be parsed: {result.stdout}.')
        return False

    # Check it meets requirements
    if py3_version < minimum_version:
        VS_PYTHON_VERSION = VerificationStatus.Failed
        logger.error(
            f'Too old of python version (3.{py3_version}) '
            f'require at least 3.{minimum_version}')
        return False

    logger.info('Python version verified.')
    VS_PYTHON_VERSION = VerificationStatus.Verified
    return True


"""
Section: FFmpeg installed
"""

VS_FFMPEG_INSTALLED = VerificationStatus.NotChecked


def is_ffmpeg_installed() -> bool:
    try:
        subprocess.run(['ffmpeg', '--version'], capture_output=True, text=True)
        return True
    except Exception:
        return False


def verify_ffmpeg_installed() -> bool:
    global VS_FFMPEG_INSTALLED

    if VS_FFMPEG_INSTALLED == VerificationStatus.Verified:
        return True
    if VS_FFMPEG_INSTALLED == VerificationStatus.Failed:
        return False

    if is_ffmpeg_installed():
        VS_FFMPEG_INSTALLED = VerificationStatus.Verified
        logger.info('FFmpeg was found.')
        return True
    else:
        VS_FFMPEG_INSTALLED = VerificationStatus.Failed
        logger.error('FFmpeg could not be found.')
        return False
