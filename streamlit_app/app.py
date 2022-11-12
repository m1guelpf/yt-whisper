import os
import subprocess
import glob
import shutil
import streamlit as st
from PIL import Image
from whisper.tokenizer import LANGUAGES

@st.cache(persist=True,allow_output_mutation=False,show_spinner=True,suppress_st_warning=True)
def clean_directory(dirpath):
    for filename in os.listdir(dirpath):
        filepath = os.path.abspath(os.path.join(dirpath, filename))
        try:
            shutil.rmtree(filepath)
        except OSError:
            os.remove(filepath)

st.set_page_config(
    page_title="Youtube - Whisper",
    page_icon="🎶",
    layout="centered",
    initial_sidebar_state="auto",
)

main_image = Image.open('static/main_banner.png')

download_path = "output/"
clean_directory(download_path)

st.image(main_image,use_column_width='auto')
st.title("✨ Automatic YouTube subtitle generation 🔊")
st.error(" 🔴 THIS IS MEANT TO BE USED FOR EDUCATIONAL PURPOSES ONLY!! 🔴")
st.info('⚠ Fetching the YouTube video and it\'s subtitles generation may take several minutes depending on the time duration, size and your choices 😉')

col1, col2, col3, col4 = st.columns(4)
with col1:
    model_type = st.radio("Please choose your model type", ('Tiny', 'Base', 'Small', 'Medium', 'Large'))
with col2:
    format_type = st.radio("Please choose your output format type", ('VTT', 'SRT'))
with col3:
    task_type = st.radio("Please choose your task type", ('Transcribe', 'Translate'))
with col4:
    language = st.selectbox('Please select the language',tuple(LANGUAGES.values()))

url = st.text_input("Enter your YouTube Video URL: 🔗")
if url is not None or url != '':
    if st.button("Fetch Video and Generate Subtitles 🚀"):
        st.video(url.strip())
        with st.spinner("Working... 💫 Meanwhile please enjoy your video 😉"):
            subprocess.run(["yt_whisper", url, "--model", model_type.lower(), "--format", format_type.lower(), "--output_dir", "output", "--verbose", "True", "--task", task_type.lower(), "--language", language.title()])

        filename = glob.glob("output/*")[0]
        output_file = open(filename,"r")
        output_file_data = output_file.read()

        if filename.endswith(".srt"):
            mime_type = "text/plain"
        else:
            mime_type = "text/vtt"

        if st.download_button(
                             label="Download Subtitles 📝",
                             data=output_file_data,
                             file_name=filename,
                             mime=mime_type
                         ):
            st.balloons()
            st.success('✅ Download Successful !!')

else:
    st.warning('⚠ Please enter the URL! 😯')


st.markdown("<br><hr><center>Made with ❤️ by <a href='mailto:ralhanprateek@gmail.com?subject=YT - Whisper WebApp!&body=Please specify the issue you are facing with the app.'><strong>Prateek Ralhan</strong></a> with the help of [yt-whisper](https://github.com/m1guelpf/yt-whisper) built by [m1guelpf](https://github.com/m1guelpf) ✨</center><hr>", unsafe_allow_html=True)
