import streamlit as st
import speech_recognition as sr
import sys

from os import path


# AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), sys.argv[1])



AUDIO_FILE = st.file_uploader("Pick your file:", ['wav', 'aiff'])

r = sr.Recognizer()
if AUDIO_FILE is not None:
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)

    try:
        # print("You said: {}\n\n".format(r.recognize_sphinx(audio)))
        st.write("{}\n\n".format(r.recognize_sphinx(audio)))
    except sr.UnknownValueError:
        st.write("Audio not understood")
    except sr.RequestError as e:
        st.write("Error {}".format(e))
