import speech_recognition as sr
from langdetect import detect_langs
import pandas as pd
import sys
import streamlit as st
from io import StringIO, BytesIO
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from datetime import datetime
import json

from os import path, listdir, environ, remove

load_dotenv()
AUDIO_FILES = st.file_uploader("Select files", ['wav'], accept_multiple_files=True)

az_api_key = environ['azureapikey']
az_region = environ['azureregion']

SCRIPT_PATH = path.dirname(path.abspath(__file__))

def sph_text_extract(the_audio, the_dict: dict) -> dict:
    r = sr.Recognizer()
    # d_bytes = BytesIO(the_audio.getvalue())
    with sr.AudioFile(the_audio) as source:
        audio = r.record(source)

    the_dict['start_time'] = datetime.now()
    recognized_text_sphinx = r.recognize_sphinx(audio)
    the_dict['end_time'] = datetime.now()
    the_dict['time_delta'] = the_dict['end_time'] - the_dict['start_time']
    the_dict['text'] = recognized_text_sphinx
    the_dict['languages'] = detect_langs(recognized_text_sphinx)
    return the_dict

def az_text_extract(the_audio, api_key: str, the_dict: dict) -> dict:
    # configure Azure cognitive speech services
    speech_config = speechsdk.SpeechConfig(subscription = az_api_key, region = az_region)
    speech_config.speech_recognition_language = "en-US"
    speech_config.endpoint_silence_timeout_ms = 25000

    audio_config = speechsdk.audio.AudioConfig(filename=the_audio)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    the_dict['start_time'] = datetime.now()
    # call the Azure speech transcription service
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    the_text_transcription = speech_recognition_result.text
    the_dict['text'] = the_text_transcription
    the_dict['end_time'] = datetime.now()
    the_dict['time_delta'] = the_dict['end_time'] - the_dict['start_time']
    the_dict['text'] = the_text_transcription
    the_dict['languages'] = detect_langs(the_text_transcription)

    return the_dict

def goog_text_extract(the_audio, api_key: str) -> str:
    pass

def aws_text_extract(the_audio, api_key: str) -> str:
    pass

def ibm_text_extract(the_audio, api_key: str) -> str:
    pass


def write_temp_file(the_file):
    with open(path.join(SCRIPT_PATH, the_file.name), "wb") as tmp_file:
        tmp_file.write(the_file.getbuffer())

def remove_temp_file(the_file):
    remove(the_file)


def main():
    pd.set_option('display.max_colwidth', None)
    r = sr.Recognizer()
    data = {'start_time': [''], 'end_time': [''], 'the_transcript': [''], 'the_languages': [''], 'time_delta': ['']}
    data_all = {'sph_the_transcript': [''], 'sph_the_languages': [''], 'az_the_transcript': [''], 'az_the_languages': ['']}
    df_sph = pd.DataFrame(data)
    df_az = pd.DataFrame(data)
    df_all = pd.DataFrame(data_all)
    df_sph.drop([0,0])
    df_az.drop([0,0])
    df_all.drop([0,0])
    n_recordings = 0
    if AUDIO_FILES is not None:
        for filename in AUDIO_FILES:
            the_dict = {}
            n_recordings += 1
            try:
                write_temp_file(filename)
                recognized_text_sphinx = sph_text_extract(path.join(SCRIPT_PATH, filename.name), the_dict)
                df_sph.loc[len(df_sph.index)] = [recognized_text_sphinx['start_time'], recognized_text_sphinx['end_time'], recognized_text_sphinx['text'], recognized_text_sphinx['time_delta'], recognized_text_sphinx['time_delta']]
                recognized_text_azure = az_text_extract(path.join(SCRIPT_PATH, filename.name), az_api_key, the_dict)
                df_az.loc[len(df_az.index)] = [recognized_text_azure['start_time'], recognized_text_azure['end_time'], recognized_text_azure['text'], recognized_text_azure['time_delta'], recognized_text_azure['time_delta']]
                remove_temp_file(path.join(SCRIPT_PATH, filename.name))
                st.write("\n\nRecording {} processed\n".format(n_recordings))
            except sr.UnknownValueError:
                st.write("Audio not understood")
            except sr.RequestError as e:
                st.write("Error {}".format(e))

            # df_sph.drop([0,0], inplace=True)
            # df_az.drop([0,0], inplace=True)
            # df_all.drop([0,0], inplace=True)
            # df_all.loc[len(df_all.index)] = [df_sph['the_transcript'][n_recordings], str(df_sph['the_languages'][n_recordings])[1:2], df_az['the_transcript'][n_recordings], str(df_az['the_languages'][n_recordings])[1:2]]

    t_sphinx, t_azure = st.tabs(["Spinx/CPU", "Azure Cognitive Speech"])
    if len(df_sph) > 0:
        with t_sphinx:
            df_sph

        with t_azure:
            df_az

if __name__ == "__main__":
    main()
