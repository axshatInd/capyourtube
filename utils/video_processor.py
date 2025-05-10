import os
import tempfile
from moviepy.editor import VideoFileClip
import subprocess

def process_video(video_path):
    """
    Process the video file and extract audio
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        tuple: (VideoFileClip object, path to extracted audio)
    """
    try:
        # Load the video
        video = VideoFileClip(video_path)
        
        # Check video duration (max 2 minutes)
        if video.duration > 120:
            raise ValueError("Video is longer than 2 minutes. Please upload a shorter video.")
        
        # Extract audio to a temporary file using FFmpeg directly
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_audio.close()
        
        # Use absolute path to FFmpeg
        ffmpeg_path = "C:\\Windows\\System32\\ffmpeg.exe"
        
        # If ffmpeg is not in System32, try common installation locations
        if not os.path.exists(ffmpeg_path):
            possible_paths = [
                "C:\\ffmpeg\\bin\\ffmpeg.exe",
                "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
                "C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe",
                os.path.expanduser("~\\ffmpeg\\bin\\ffmpeg.exe")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    ffmpeg_path = path
                    break
        
        # Use FFmpeg directly to extract audio
        ffmpeg_cmd = [
            ffmpeg_path, '-i', video_path, 
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian format
            '-ar', '16000',  # 16kHz sample rate (good for speech recognition)
            '-ac', '1',  # Mono channel
            '-y',  # Overwrite output file if it exists
            temp_audio.name
        ]
        
        # Run FFmpeg command
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        
        # Verify the file exists and has content
        if not os.path.exists(temp_audio.name) or os.path.getsize(temp_audio.name) == 0:
            raise Exception(f"Failed to extract audio to {temp_audio.name}")
            
        return video, temp_audio.name
    except Exception as e:
        raise Exception(f"Error processing video: {str(e)}")