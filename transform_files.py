import os
import math
from moviepy.editor import VideoFileClip
from pydub import AudioSegment


def split_video_to_audio_segments(video_path, segment_length_mins=5, output_dir="output"):
    """
    Split a video file into wav audio segments of specified length.

    Parameters:
    video_path (str): Path to the input video file
    segment_length_mins (int): Length of each audio segment in minutes
    output_dir (str): Directory to save the output audio segments
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Extract filename without extension
    base_filename = os.path.splitext(os.path.basename(video_path))[0]
    print(base_filename)

    # Convert video to audio
    print("Extracting audio from video...")
    video = VideoFileClip(video_path)
    audio = video.audio

    # Save as temporary WAV file (needed for pydub)
    temp_folder = os.path.join(output_dir, base_filename)
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    temp_wav = os.path.join(temp_folder, "temp_audio.wav")
    audio.write_audiofile(temp_wav)
    video.close()

    # Load audio file using pydub
    print("Loading audio file...")
    audio_segment = AudioSegment.from_wav(temp_wav)

    # Calculate segment length in milliseconds
    segment_length_ms = segment_length_mins * 60 * 1000
    total_segments = math.ceil(len(audio_segment) / segment_length_ms)

    print(f"Splitting audio into {total_segments} segments...")

    file_paths = []
    # responses = []
    # # Split and export segments
    for i in range(total_segments):
        start_time = i * segment_length_ms
        end_time = min((i + 1) * segment_length_ms, len(audio_segment))

        # Extract segment
        segment = audio_segment[start_time:end_time]

        # Export as wav
        name = f"{base_filename +'_' + str(i)}.wav"
        output_path = os.path.join(output_dir, name)

        segment.export(output_path, format="wav")
        print(output_path)
        file_paths.append(output_path)

        print(f"Created segment {i} of {total_segments}: {output_path}")
    os.remove(temp_wav)
    os.removedirs(temp_folder)
    print("Audio splitting complete!")
    return file_paths
