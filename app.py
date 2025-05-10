import os
import tempfile
import streamlit as st
import moviepy_config  # Add this line to load the ImageMagick configuration
from utils.video_processor import process_video
from utils.speech import transcribe_audio, generate_voiceover
from utils.caption import add_captions_to_video

# Set page configuration
st.set_page_config(
    page_title="CapYourTube",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    css_path = os.path.join("static", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Try to load CSS if it exists
try:
    load_css()
except:
    pass

# Check if Vosk model exists, if not show download instructions
model_path = os.path.join("models", "vosk-model-en-us-0.22")
if not os.path.exists(model_path):
    st.warning("""
    ### First-time setup required
    
    You need to download the Vosk speech recognition model for offline use.
    
    1. Create a 'models' folder in the project directory
    2. Download the model from https://alphacephei.com/vosk/models (vosk-model-en-us-0.22.zip)
    3. Extract the zip file into the 'models' folder
    4. Restart the application
    
    You only need to do this once.
    
    Note: This is a larger model (1.8GB) with better accuracy than the small model.
    """)

# App header
st.title("🎬 CapYourTube")
st.markdown("### Create captioned videos with AI voiceover - 100% Offline!")

# Create columns for a better layout - main controls and preview area
col1, col2 = st.columns([1, 1])

with col1:
    # File uploader
    uploaded_file = st.file_uploader("Upload your video (MP4 format, max 2 minutes)", type=["mp4"])
    
    # Text input for custom script
    custom_script = st.text_area(
        "Enter custom script (leave empty for auto-transcription)",
        height=150
    )
    
    # Voice selection
    voice_option = st.selectbox(
        "Select voice type",
        ["Default", "Male", "Female"]
    )
    
    # Caption style options
    caption_style = st.selectbox(
        "Caption style",
        ["Modern", "Classic", "Minimal"]
    )
    
    # Caption position
    caption_position = st.selectbox(
        "Caption position",
        ["Bottom", "Top", "Center"]
    )
    
    # Process button
    process_button = st.button("Process Video", type="primary")

with col2:
    # Create two columns for original and processed video previews
    preview_col1, preview_col2 = st.columns(2)
    
    with preview_col1:
        st.markdown("### Original")
        original_preview = st.empty()
        
        if uploaded_file is None:
            original_preview.info("Upload a video")
    
    with preview_col2:
        st.markdown("### Captioned")
        captioned_preview = st.empty()
        captioned_preview.info("Process to see result")
    
    # Status area for processing messages
    status_area = st.empty()
    
    if uploaded_file is not None:
        # Save uploaded file to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.write(uploaded_file.read())
        temp_file.close()
        
        # Display the uploaded video
        original_preview.video(temp_file.name)
        
        if process_button:
            with st.spinner("Processing your video..."):
                try:
                    # Step 1: Transcribe if no custom script
                    status_area.info("Transcribing audio (offline)...")
                    if not custom_script:
                        custom_script = transcribe_audio(temp_file.name, model_path)
                        status_area.success(f"Transcription complete: {custom_script}")
                    
                    # Step 2: Generate voiceover
                    status_area.info("Generating voiceover (offline)...")
                    voiceover_path = generate_voiceover(custom_script, voice_type=voice_option.lower())
                    
                    # Step 3: Add captions to video
                    status_area.info("Adding captions...")
                    output_path = add_captions_to_video(
                        temp_file.name, 
                        custom_script, 
                        voiceover_path,
                        style=caption_style.lower(),
                        position=caption_position.lower()
                    )
                    
                    # Step 4: Display the result
                    status_area.success("Video processing complete!")
                    captioned_preview.video(output_path)
                    
                    # Download button
                    st.download_button(
                        label="Download Captioned Video",
                        data=open(output_path, "rb").read(),
                        file_name="captioned_video.mp4",
                        mime="video/mp4"
                    )
                        
                except Exception as e:
                    status_area.error(f"An error occurred: {str(e)}")
                
                # Clean up
                try:
                    os.unlink(temp_file.name)
                except:
                    pass

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Python | 100% Offline - No Internet Required")