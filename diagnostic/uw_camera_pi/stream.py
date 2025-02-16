from typing import TypedDict, Any
import subprocess
import ffmpeg  # type: ignore


def default_prompt(prompt: str, default: str) -> str:
    res = input(f'prompt ({default}): ')
    return res if len(res) else default


def yes_no_prompt(prompt: str) -> bool:
    res = input(f'{prompt} (y|n): ')
    return res.lower() in ['y', 'yes']


def construct_stream_url(rtsp_server: str, stream_name: str):
    return f'rtsp://{rtsp_server}/{stream_name}'


"""
Start streaming
"""


class StartStreamConfigs(TypedDict):
    rtsp_server: str
    stream_name: str
    stream_src: str
    is_file_stream: bool


def prompt_start_stream_configs() -> StartStreamConfigs:
    return dict(
        rtsp_server=default_prompt('Address of RTSP server', 'localhost:8554'),
        stream_name=default_prompt('Name of stream', 'live.stream'),
        stream_src=input('Stream source: '),
        is_file_stream=yes_no_prompt('Is file stream')
    )


def start_stream(configs: StartStreamConfigs):
    input_kwargs: dict[str, Any] = {
        're': None
    }

    output_kwargs: dict[str, Any] = {
        'vcodec': 'libx264',
        'bf': 0,
        'preset': 'ultrafast',
        'tune': 'zerolatency',
        'f': 'rtsp',
        'rtsp_transport': 'tcp'
    }

    if configs['is_file_stream']:
        input_kwargs['stream_loop'] = -1

    (ffmpeg
        .input(
            configs['stream_src'],
            **input_kwargs
            )
        .output(
            construct_stream_url(configs['rtsp_server'], configs['stream_name']),
            **output_kwargs
        )
        .run())


"""
Play stream
"""


class PlayStreamConfigs(TypedDict):
    rtsp_server: str
    stream_name: str


def prompt_play_stream_configs() -> PlayStreamConfigs:
    return dict(
        rtsp_server=default_prompt('Address of RTSP server', 'localhost:8554'),
        stream_name=default_prompt('Name of stream', 'live.stream'),
    )


def play_stream(configs: PlayStreamConfigs):
    command = ['ffplay',
               '-vcodec', 'h264',
               '-rtsp_transport', 'tcp',
               construct_stream_url(configs['rtsp_server'], configs['stream_name'])]

    try:
        subprocess.run(command).check_returncode()
    except Exception as e:
        print(e)


"""
Manager
"""

if __name__ == "__main__":
    choice = input('Start or Play (S|P): ').lower()

    if choice == 's':
        start_stream(prompt_start_stream_configs())
    elif choice == 'p':
        play_stream(prompt_play_stream_configs())
    else:
        print(f"Invalid option provided: {choice}.")
