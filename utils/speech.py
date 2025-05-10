import os
import tempfile
import json
import wave
import pyttsx3
from vosk import Model, KaldiRecognizer
import subprocess

def transcribe_audio(video_path, model_path):
    """
    Transcribe audio from a video file using Vosk (offline)
    
    Args:
        video_path (str): Path to the video file
        model_path (str): Path to the Vosk model
        
    Returns:
        str: Transcribed text
    """
    try:
        # Extract audio from video
        from utils.video_processor import process_video
        _, audio_path = process_video(video_path)
        
        # Check if model exists
        if not os.path.exists(model_path):
            return "Error: Speech recognition model not found. Please download the Vosk model."
        
        # Verify audio file exists
        if not os.path.exists(audio_path):
            return f"Error: Audio file not found at {audio_path}"
            
        # Load model
        model = Model(model_path)
        
        try:
            # Open audio file
            wf = wave.open(audio_path, "rb")
        except Exception as e:
            # If wave.open fails, try to convert the file again with FFmpeg
            temp_compatible = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_compatible.close()
            
            ffmpeg_cmd = [
                'ffmpeg', '-i', audio_path, 
                '-acodec', 'pcm_s16le',
                '-ar', '16000', 
                '-ac', '1',
                '-y',
                temp_compatible.name
            ]
            
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            audio_path = temp_compatible.name
            wf = wave.open(audio_path, "rb")
        
        # Check if audio format is compatible
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            # Convert to compatible format if needed
            temp_compatible = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_compatible.close()
            
            ffmpeg_cmd = [
                'ffmpeg', '-i', audio_path, 
                '-acodec', 'pcm_s16le',
                '-ar', '16000', 
                '-ac', '1',
                '-y',
                temp_compatible.name
            ]
            
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            wf.close()
            wf = wave.open(temp_compatible.name, "rb")
        
        # Create recognizer
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        
        # Process audio
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                part_result = json.loads(rec.Result())
                results.append(part_result.get('text', ''))
        
        part_result = json.loads(rec.FinalResult())
        results.append(part_result.get('text', ''))
        
        # Clean up
        wf.close()
        try:
            os.unlink(audio_path)
        except:
            pass
        
        # Join all parts
        transcript = ' '.join([r for r in results if r])
        
        return transcript if transcript else "No speech detected"
    except Exception as e:
        return f"Failed to transcribe audio: {str(e)}"

def generate_voiceover(text, voice_type="default"):
    """
    Generate AI voiceover from text using pyttsx3 (offline)
    
    Args:
        text (str): Text to convert to speech
        voice_type (str): Type of voice to use
        
    Returns:
        str: Path to the generated audio file
    """
    try:
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        
        # Set voice based on selection
        if voice_type == "male" and len(voices) > 0:
            # Find a male voice
            for voice in voices:
                if "male" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
        elif voice_type == "female" and len(voices) > 0:
            # Find a female voice
            for voice in voices:
                if "female" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
        
        # Set properties
        engine.setProperty('rate', 150)  # Speed
        engine.setProperty('volume', 0.9)  # Volume
        
        # Save to temporary file
        temp_tts = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_tts.close()
        
        engine.save_to_file(text, temp_tts.name)
        engine.runAndWait()
        
        # Verify the file exists
        if not os.path.exists(temp_tts.name) or os.path.getsize(temp_tts.name) == 0:
            raise Exception(f"Failed to generate voiceover file at {temp_tts.name}")
            
        return temp_tts.name
    except Exception as e:
        raise Exception(f"Error generating voiceover: {str(e)}")