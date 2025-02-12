from typing import Any
import subprocess
import logging
import json

logger = logging.getLogger('Default')

"""
This program uses v4l2-ctl "Video for linux" to find information about cameras.

The `v4l2-ctl --list-devices` command will list all cameras and their devices.
    Most cameras will have multiple devices.

The `v4l2-ctl --device=<device-name> --all` list all information about a specific device
such as "/dev/media0" for example.

Honestly, I was pretty lazy, so this only grabs the fields listed in FIELDS_OF_INTEREST rather than
parsing every single line in the file.
"""


FIELDS_OF_INTEREST = [
        'Width/Height',
        'Pixel Format',
        'Colorspace',
        'Frames per second'
    ]


class Camera(object):
    def __init__(self, name: str, platform: str, devices: list[str]):
        self.name = name
        self.platform = platform
        self.devices = [Device(name) for name in devices]

    def to_json(self) -> dict[str, Any]:
        return dict(
            name=self.name,
            platform=self.platform,
            devices=[device.to_json() for device in self.devices]
        )

    def __str__(self) -> str:
        return f'Camera({self.to_json()})'

    def __repr__(self) -> str:
        return str(self)


class Device(object):
    def __init__(self, device: str):
        self.name = device
        self.fields: dict[str, str] = {}

        self._parse_fields_of_interest()

    def to_json(self) -> dict[str, Any]:
        return dict(
            name=self.name,
            fields=self.fields
        )

    def __str__(self) -> str:
        return f'Device({self.to_json()})'

    def __repr__(self) -> str:
        return str(self)

    def _parse_fields_of_interest(self):
        try:
            result = subprocess.run(['v4l2-ctl', f'--device={self.name}', '--all'],
                                    capture_output=True,
                                    text=True)
            result.check_returncode()
        except Exception:
            logger.error(f'Failed to list info about device {self.name}.')

        output = result.stdout.splitlines()

        def parse_field_value(line: str):
            # just in case colons are in the value
            line = ':'.join(line.split(':')[1:])
            return line.strip()

        for line in output:
            for field in FIELDS_OF_INTEREST:
                if field in line:
                    self.fields[field] = parse_field_value(line)


def list_cameras() -> list[Camera]:
    try:
        result = subprocess.run(['v4l2-ctl', '--list-devices'],
                                capture_output=True,
                                text=True)
        result.check_returncode()
    except Exception:
        logger.error('Failed to list devices.')
        return []

    def split_cameras(output: str) -> list[list[str]]:
        cameras: list[list[str]] = []
        camera: list[str] = []

        for line in output.splitlines():
            if len(line):
                camera.append(line)
            else:
                if len(camera):
                    cameras.append(camera)
                    camera = []
        if len(camera):
            cameras.append(camera)

        return cameras

    def parse_camera(output: list[str]) -> Camera:
        camera_id_line = output[0]
        camera_name = camera_id_line.split('(')[0].strip()
        camera_platform = camera_id_line.split('(')[1].split(')')[0].strip()        
        devices = [line.strip() for line in output[1:] if '/dev/media' not in line]
        return Camera(camera_name, camera_platform, devices)

    cameras = split_cameras(result.stdout)
    logger.info(f'Identified {len(cameras)} cameras.')
    return [parse_camera(camera) for camera in cameras]


if __name__ == "__main__":
    cameras = list_cameras()
    cameras_json = [camera.to_json() for camera in cameras]
    with open('summary.json', 'w') as file_json:
        json.dump(cameras_json, file_json, indent=4)
