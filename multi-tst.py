import speech_recognition as sr
from langdetect import detect_langs
import pandas as pd
import sys
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

from os import path, listdir, environ

load_dotenv()
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), sys.argv[1])

az_api_key = environ['azureapikey']
az_region = environ['azureregion']

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

def main(the_path: str):
    pd.set_option('display.max_colwidth', None)
    r = sr.Recognizer()
    data = {'the_transcript': [''], 'the_languages': ['']}
    data_all = {'sph_the_transcript': [''], 'sph_the_languages': [''], 'az_the_transcript': [''], 'az_the_languages': ['']}
    df_sph = pd.DataFrame(data)
    df_az = pd.DataFrame(data)
    df_all = pd.DataFrame(data_all)
    n_recordings = 0
    for filename in listdir(the_path):
        n_recordings += 1
        if filename.endswith(".wav"):
            with sr.AudioFile(path.join(the_path, filename)) as source:
                audio = r.record(source)
            try:
                recognized_text_sphinx = r.recognize_sphinx(audio)
                recognized_text_azure = az_text_extract(path.join(the_path, filename), az_api_key)
                df_sph.loc[len(df_sph)] = [recognized_text_sphinx, detect_langs(recognized_text_sphinx)]
                df_az.loc[len(df_az)] = [recognized_text_azure, detect_langs(recognized_text_azure)]
            except sr.UnknownValueError:
                print("Audio not understood")
            except sr.RequestError as e:
                print("Error {}".format(e))

        df_all.loc[len(df_all)] = [df_sph['the_transcript'], df_sph['the_languages'], df_az['the_transcript'], df_az['the_languages']]

    for i in range(1, len(df_all)):
        print("\n{} |--| {} : {} >----< {}\n".format(df_all.loc[i]['sph_the_transcript'], df_all.loc[i]['sph_the_languages'], df_all.loc[i]['az_the_transcript'], df_all.loc[i]['az_the_languages']))
    df_all.info()


if __name__ == "__main__":
    main(sys.argv[1])
