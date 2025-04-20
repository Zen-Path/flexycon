#!/usr/bin/env python3

import os
import subprocess

# Define the input file and yt-dlp options
input_file = "audio_list.txt"
yt_dlp_options = [
    "yt-dlp",
    "--embed-metadata",
    "-i",
    "--no-playlist",
    "--extract-audio",
    "--format",
    "bestaudio/best",
]

# Read the input file
try:
    with open(input_file, "r") as file:
        lines = file.readlines()
except FileNotFoundError:
    print(f"Error: {input_file} not found.")
    exit(1)

# Process each line in the file
for line in lines:
    line = line.strip()
    if not line:
        continue  # Skip empty lines

    # Extract the path and video ID
    try:
        video_id_start = line.rindex("[") + 1
        video_id_end = line.rindex("]")
        video_id = line[video_id_start:video_id_end]

        output_path = os.path.dirname(line)
        file_name = os.path.basename(line)

        # Run yt-dlp command
        command = yt_dlp_options + [
            f"https://www.youtube.com/watch?v={video_id}",
            "--output",
            os.path.join(output_path, file_name),
        ]

        print(f"Downloading: {file_name} to {output_path}")
        subprocess.run(command, check=True)
    except Exception as e:
        print(f"Failed to process line: {line}\nError: {e}")

print("Download process completed.")
