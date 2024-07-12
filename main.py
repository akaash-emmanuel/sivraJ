import time
import playsound
from gtts import gTTS
import openai
import speech_recognition as sr
import os


api_key = 'sk-proj-bHgxM433ykB0nj2rVtApT3BlbkFJwb30IgttvYKnBYsyjcTc'
openai.api_key = api_key

# Language for text-to-speech
lang = 'en'

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)                    #change source as per device for microphone port
        said = ""

        try:
            said = r.recognize_google_cloud(audio)
            print(f"Recognized: {said}")

            if "tool" in said.lower():
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": said}]
                )
                text = completion.choices[0].message.content
                print(f"GPT-3.5 Response: {text}")


                filename = f"response_{int(time.time())}.mp3"
                speech = gTTS(text=text, lang=lang, slow=False, tld="com.au")
                speech.save(filename)
                playsound.playsound(filename)

            # check for command to stop
            elif "stop" in said.lower():
                print("Stopping the loop.")
                return None

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio.")
        except sr.RequestError as e:
            print(f"Request Error: {e}")
        except openai.OpenAIError as e:
            print(f"OpenAI API Error: {e}")
        except Exception as e:
            print(f"General Exception: {e}")

    return said


while True:
    result = get_audio()
    if result is None:
        break
    time.sleep(1)
