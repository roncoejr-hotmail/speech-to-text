import speech_recognition as sr
from langdetect import detect_langs
import pandas as pd
import sys
import streamlit as st
from io import StringIO, BytesIO

from os import path, listdir


AUDIO_FILES = st.file_uploader("Select files", ['wav'], accept_multiple_files=True)

pd.set_option('display.max_colwidth', None)
r = sr.Recognizer()
data = {'the_transcript': [''], 'the_languages': ['']}
df = pd.DataFrame(data)
n_recordings = 0
if AUDIO_FILES is not None:
    for filename in AUDIO_FILES:
        n_recordings += 1
        d_bytes = BytesIO(filename.getvalue())
        with sr.AudioFile(d_bytes) as source:
            audio = r.record(source)


        try:
            recognized_text = r.recognize_sphinx(audio)
            df.loc[len(df)] = [recognized_text, detect_langs(recognized_text)]
            st.write("\n\nRecording {} processed\n".format(n_recordings))
        except sr.UnknownValueError:
            st.write("Audio not understood")
        except sr.RequestError as e:
            st.write("Error {}".format(e))

df
df.info()
