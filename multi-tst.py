import speech_recognition as sr
from langdetect import detect_langs
import pandas as pd
import sys

from os import path, listdir


AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), sys.argv[1])

pd.set_option('display.max_colwidth', None)
r = sr.Recognizer()
data = {'the_transcript': [''], 'the_languages': ['']}
df = pd.DataFrame(data)
n_recordings = 0
for filename in listdir(sys.argv[1]):
    n_recordings += 1
    if filename.endswith(".wav") or filename.endswith(".aif"):
        with sr.AudioFile(path.join(sys.argv[1], filename)) as source:
            audio = r.record(source)


        try:
            recognized_text = r.recognize_sphinx(audio)
            df.loc[len(df)] = [recognized_text, detect_langs(recognized_text)]
            print("\n\nRecording {} processed\n".format(n_recordings))
        except sr.UnknownValueError:
            print("Audio not understood")
        except sr.RequestError as e:
            print("Error {}".format(e))


# print("\n\n\nThe transcript reads: {}\n\nLanguage(s) Detected: {}\n\n".format(recognized_text, detect_langs(recognized_text)))
# print("{}\n".format(df.head()))
for i in range(1, len(df)):
    print("\n{} |--| {}\n".format(df.loc[i]['the_transcript'], df.loc[i]['the_languages']))
df.info()
