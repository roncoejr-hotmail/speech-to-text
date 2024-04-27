import speech_recognition as sr
import sys

from os import path


AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), sys.argv[1])


r = sr.Recognizer()

with sr.AudioFile(AUDIO_FILE) as source:
    audio = r.record(source)


try:
    print("You said: {}\n\n".format(r.recognize_sphinx(audio)))
except sr.UnknownValueError:
    print("Audio not understood")
except sr.RequestError as e:
    print("Error {}".format(e))
