import os
import time
import pygame
from gtts import gTTS
import speech_recognition as sr
import openai
import taipy as tp

# custom OpenAI class
class OpenAI:
    def __init__(self, api_key):
        openai.api_key = api_key

    def chat_completion(self, model, messages):
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        return response

# initialize with openai key
api_key = 'sk-proj-bHgxM433ykB0nj2rVtApT3BlbkFJwb30IgttvYKnBYsyjcTc'
client = OpenAI(api_key=api_key)

lang = 'en'

pygame.init()
pygame.mixer.init()

# display
width, height = 400, 300
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Voice Assistant")


WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# font
font = pygame.font.Font(None, 36)

def draw_text(text, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def save_audio_file(audio):
    filename = f"input_{int(time.time())}.wav"
    with open(filename, "wb") as f:
        f.write(audio.get_wav_data())
    return filename

def process_audio(audio_file):
    print(f"Processing audio file: {audio_file}")
    return audio_file

def generate_text_response(audio_file):
    print(f"Generating text response for: {audio_file}")
    # convert audio file to text
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = r.record(source)
        said = r.recognize_google(audio_data)

    # get response from gpt
    response = client.chat_completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": said}]
    )
    text = response.choices[0].message.content
    print(f"GPT-3.5 Response: {text}")
    return text

def text_to_speech(text):
    print(f"Converting text to speech: {text}")
    response_filename = f"response_{int(time.time())}.mp3"
    speech = gTTS(text=text, lang=lang, slow=False, tld="com.au")
    speech.save(response_filename)
    return response_filename

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        said = ""

        try:
            # save audio to file
            audio_filename = save_audio_file(audio)
            print(f"Audio saved to {audio_filename}")

            # process audio file
            processed_audio = process_audio(audio_filename)

            # generate text response
            text = generate_text_response(processed_audio)

            # convert text to speech and save
            response_filename = text_to_speech(text)

            # load and play the audio response
            pygame.mixer.music.load(response_filename)
            pygame.mixer.music.play()

            # display the response text on the screen
            screen.fill(WHITE)
            draw_text("Response: " + text, GREEN, screen, width // 2, height // 2)
            pygame.display.flip()

            # wait until the sound finishes playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio.")
            screen.fill(WHITE)
            draw_text("Error: Could not understand audio", RED, screen, width // 2, height // 2)
            pygame.display.flip()
        except sr.RequestError as e:
            print(f"Request Error: {e}")
            screen.fill(WHITE)
            draw_text("Error: Request failed", RED, screen, width // 2, height // 2)
            pygame.display.flip()
        except openai.OpenAIError as e:
            print(f"OpenAI API Error: {e}")
            screen.fill(WHITE)
            draw_text("Error: OpenAI API issue", RED, screen, width // 2, height // 2)
            pygame.display.flip()
        except Exception as e:
            print(f"General Exception: {e}")
            screen.fill(WHITE)
            draw_text("Error: General exception", RED, screen, width // 2, height // 2)
            pygame.display.flip()

    return said

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    result = get_audio()
    if result is None:
        running = False

    time.sleep(1) 

pygame.quit()
