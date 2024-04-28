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
import boto3
import time
import requests



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

def aws_text_extract(the_audio, the_dict: dict) -> dict:
    transcribe_client = boto3.client("transcribe")
    s3_client = boto3.client('s3')
    file_uri_base = environ['s3root']
    file_uri_path = environ['s3path']
    the_job_name = "SUPRT_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    s3_client.upload_file(the_audio, file_uri_base, file_uri_path + "/" + the_job_name + ".wav")
    file_uri = file_uri_base + "/" + file_uri_path + "/" + the_job_name + ".wav"
    the_dict = aws_text_extract_callback(the_job_name, the_audio, file_uri, the_dict, transcribe_client)
    return the_dict

def aws_text_extract_callback(job_name: str, the_audio, file_uri, the_dict: dict, transcribe_client) -> dict:
    transcribe_client.start_transcription_job(TranscriptionJobName=job_name, Media={"MediaFileUri": "s3://" + file_uri}, MediaFormat="wav", LanguageCode="en-US",)

    the_dict['start_time'] = datetime.now()
    # st.write("Set max tries")
    max_tries = 60

    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job["TranscriptionJob"]["TranscriptionJobStatus"]
        if job_status in ["COMPLETED", "FAILED"]:
            # st.write(f"Job {job_name} is {job_status}.")
            if job_status == "COMPLETED":
                # st.write(f"{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}.")
                s3_obj = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
                # TODO: Download the file
                s3_client = boto3.client('s3')
                t_response = requests.get(job['TranscriptionJob']['Transcript']['TranscriptFileUri'])
                t_transcript = json.loads(t_response.content)
                # s3_client.download_file(environ['s3root'], s3_obj, job_name + ".json")
                # TODO: Set dictionary attributes
                the_dict['text'] = t_transcript['results']['transcripts'][0]['transcript']
                the_dict['end_time'] = datetime.now()
                the_dict['time_delta'] = the_dict['end_time'] - the_dict['start_time']
                # the_dict['languages'] = detect_langs(the_text_transcription)
                the_dict['languages'] = "TBC"
                # Return the dictionary
                # return the_dict
                break
            else:
                st.write(f"{job_name}.  Current status is {job_status}.")
        else:
            st.write(f"{job_status}.")
            time.sleep(10)


    return the_dict


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
    df_aws = pd.DataFrame(data)
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
                df_sph.loc[len(df_sph.index)] = [recognized_text_sphinx['start_time'], recognized_text_sphinx['end_time'], recognized_text_sphinx['text'], recognized_text_sphinx['languages'][1:2], recognized_text_sphinx['time_delta']]
                recognized_text_azure = az_text_extract(path.join(SCRIPT_PATH, filename.name), az_api_key, the_dict)
                df_az.loc[len(df_az.index)] = [recognized_text_azure['start_time'], recognized_text_azure['end_time'], recognized_text_azure['text'], recognized_text_azure['languages'][1:2], recognized_text_azure['time_delta']]
                recognized_text_aws = aws_text_extract(path.join(SCRIPT_PATH, filename.name), the_dict)
                df_aws.loc[len(df_aws.index)] = [recognized_text_aws['start_time'], recognized_text_aws['end_time'], recognized_text_aws['text'], recognized_text_aws['languages'][1:2], recognized_text_aws['time_delta']]
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

    t_sphinx, t_azure, t_aws = st.tabs(["Spinx/CPU", "Azure Cognitive Speech", "AWS Transcription"])
    if len(df_sph) > 0:
        with t_sphinx:
            df_sph

        with t_azure:
            df_az
        
        with t_aws:
            df_aws

if __name__ == "__main__":
    main()
