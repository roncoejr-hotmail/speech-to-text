import speech_recognition as sr
from langdetect import detect_langs
import pandas as pd
import sys

from os import path


AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), sys.argv[1])


r = sr.Recognizer()
data = {'the_transcript': [''], 'the_languages': ['']}
df = pd.DataFrame(data)
with sr.AudioFile(AUDIO_FILE) as source:
    audio = r.record(source)


try:
    recognized_text = r.recognize_sphinx(audio)
    # print("\n\n\nThe transcript reads: {}\n\nLanguage(s) Detected: {}\n\n".format(recognized_text, detect_langs(recognized_text)))
    df.loc[len(df)] = [recognized_text, detect_langs(recognized_text)]
    print("{}".format(df.head()))
    df.info()
except sr.UnknownValueError:
    print("Audio not understood")
except sr.RequestError as e:
    print("Error {}".format(e))
