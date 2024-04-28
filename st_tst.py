import speech_recognition as sr
from langdetect import detect_langs
import pandas as pd
import sys
import streamlit as st
from io import StringIO, BytesIO
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

from os import path, listdir, environ

load_dotenv()
AUDIO_FILES = st.file_uploader("Select files", ['wav'], accept_multiple_files=True)

az_api_key = environ['azureapikey']
az_region = environ['azureregion']

SCRIPT_PATH = path.dirname(path.abspath(__file__))

def az_text_extract(the_audio, api_key: str) -> str:
    # configure Azure cognitive speech services
    speech_config = speechsdk.SpeechConfig(subscription = az_api_key, region = az_region)
    speech_config.speech_recognition_language = "en-US"
    speech_config.endpoint_silence_timeout_ms = 25000

    audio_config = speechsdk.audio.AudioConfig(filename=the_audio)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    # call the Azure speech transcription service
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    the_text_transcription = speech_recognition_result.text

    # return the transcribed text
    return the_text_transcription

def write_temp_file(the_file):
    with open(path.join(SCRIPT_PATH, the_file.name), "wb") as tmp_file:
        tmp_file.write(the_file.getbuffer())


def main():
    pd.set_option('display.max_colwidth', None)
    r = sr.Recognizer()
    data = {'the_transcript': [''], 'the_languages': ['']}
    data_all = {'sph_the_transcript': [''], 'sph_the_languages': [''], 'az_the_transcript': [''], 'az_the_languages': ['']}
    df_sph = pd.DataFrame(data)
    df_az = pd.DataFrame(data)
    df_all = pd.DataFrame(data_all)
    n_recordings = 0
    if AUDIO_FILES is not None:
        for filename in AUDIO_FILES:
            n_recordings += 1
            d_bytes = BytesIO(filename.getvalue())
            with sr.AudioFile(d_bytes) as source:
                audio = r.record(source)
            try:
                recognized_text_sphinx = r.recognize_sphinx(audio)
                write_temp_file(filename)
                recognized_text_azure = az_text_extract(path.join(SCRIPT_PATH, filename.name), az_api_key)
                df_sph.loc[len(df_sph.index)] = [recognized_text_sphinx, detect_langs(recognized_text_sphinx)]
                df_az.loc[len(df_az.index)] = [recognized_text_azure, detect_langs(recognized_text_azure)]
                st.write("\n\nRecording {} processed\n".format(n_recordings))
            except sr.UnknownValueError:
                st.write("Audio not understood")
            except sr.RequestError as e:
                st.write("Error {}".format(e))

            df_all.loc[len(df_all.index)] = [df_sph['the_transcript'][n_recordings], df_sph['the_languages'][n_recordings], df_az['the_transcript'][n_recordings], df_az['the_languages'][n_recordings]]

    df_all
    df_all.info()



if __name__ == "__main__":
    main()
