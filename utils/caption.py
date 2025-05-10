import os
import tempfile
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
import numpy as np

def add_captions_to_video(video_path, caption_text, voiceover_path, style="modern", position="bottom"):
    """
    Add captions and voiceover to a video
    
    Args:
        video_path (str): Path to the video file
        caption_text (str): Text to display as captions
        voiceover_path (str): Path to the voiceover audio file
        style (str): Caption style (modern, classic, minimal)
        position (str): Caption position (bottom, top, center)
        
    Returns:
        str: Path to the output video file
    """
    try:
        # Load the video
        video = VideoFileClip(video_path)
        
        # Load the voiceover
        voiceover = AudioFileClip(voiceover_path)
        
        # Set style parameters
        if style == "modern":
            fontsize = 30
            color = 'white'
            bg_color = 'rgba(0,0,0,0.5)'
            font = 'Arial'
            stroke_color = 'black'
            stroke_width = 1
        elif style == "classic":
            fontsize = 28
            color = 'yellow'
            bg_color = None
            font = 'Arial-Bold'
            stroke_color = 'black'
            stroke_width = 2
        else:  # minimal
            fontsize = 24
            color = 'white'
            bg_color = None
            font = 'Arial'
            stroke_color = 'black'
            stroke_width = 1
        
        # Set position
        if position == "bottom":
            pos = ('center', 'bottom')
        elif position == "top":
            pos = ('center', 'top')
        else:  # center
            pos = 'center'
        
        # Create text clip
        txt_clip = TextClip(
            caption_text, 
            fontsize=fontsize, 
            color=color, 
            bg_color=bg_color,
            font=font,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            method='caption',
            size=(video.w * 0.9, None)
        )
        
        # Set position and duration
        txt_clip = txt_clip.set_position(pos).set_duration(video.duration)
        
        # Combine video with captions
        final_clip = CompositeVideoClip([video, txt_clip])
        
        # Set audio to the voiceover (if it fits) or keep original
        if voiceover.duration >= video.duration:
            voiceover = voiceover.subclip(0, video.duration)
            final_clip = final_clip.set_audio(voiceover)
        else:
            # Extend voiceover to match video duration by adding silence
            from pydub import AudioSegment
            import numpy as np
            
            # Convert voiceover to numpy array
            voiceover_array = voiceover.to_soundarray()
            
            # Calculate how many samples we need to add
            sample_rate = 44100  # Standard sample rate
            current_samples = voiceover_array.shape[0]
            needed_samples = int(video.duration * sample_rate) - current_samples
            
            if needed_samples > 0:
                # Create silence array
                silence = np.zeros((needed_samples, 2))
                
                # Concatenate with voiceover
                extended_audio = np.vstack([voiceover_array, silence])
                
                # Create new AudioClip
                from moviepy.audio.AudioClip import AudioArrayClip
                new_audio = AudioArrayClip(extended_audio, fps=sample_rate)
                
                # Set as video audio
                final_clip = final_clip.set_audio(new_audio)
        
        # Save the final video
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, fps=video.fps)
        
        # Clean up
        os.unlink(voiceover_path)
        
        return output_path
    except Exception as e:
        raise Exception(f"Error adding captions: {str(e)}")