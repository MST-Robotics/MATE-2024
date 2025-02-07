#!/bin/bash
ffmpeg -re -stream_loop -1 -i donny.mp4 -vcodec libx264 -bf 0 -f rtsp -rtsp_transport tcp rtsp://localhost:8554/live.stream
