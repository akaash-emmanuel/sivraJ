import os
import time
import pygame
from gtts import gTTS
import speech_recognition as sr
import openai

# Custom OpenAI class
class OpenAI:
    def __init__(self, api_key):
        openai.api_key = api_key

    def chat_completion(self, model, messages):
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        return response

# Initialize OpenAI with your API key
api_key = 'sk-proj-bHgxM433ykB0nj2rVtApT3BlbkFJwb30IgttvYKnBYsyjcTc'
client = OpenAI(api_key=api_key)

# Language for text-to-speech
lang = 'en'

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer module

# Set up the display
width, height = 400, 300
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Voice Assistant")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Font
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


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        said = ""

        try:
            # Save the recorded audio to a file
            audio_filename = save_audio_file(audio)
            print(f"Audio saved to {audio_filename}")

            # Convert audio file to text
            with sr.AudioFile(audio_filename) as source:
                audio_data = r.record(source)
                said = r.recognize_google(audio_data)
                print(f"Recognized: {said}")

            if "shivraj" in said.lower():
                print("Keyword detected: shivraj")

                # Request response from GPT-3.5
                response = client.chat_completion(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": said}]
                )
                text = response['choices'][0]['message']['content']
                print(f"GPT-3.5 Response: {text}")

                if text:
                    # Save response as an audio file
                    response_filename = f"response_{int(time.time())}.mp3"
                    speech = gTTS(text=text, lang=lang, slow=False, tld="com.au")
                    speech.save(response_filename)
                    print(f"Response saved to {response_filename}")

                    # Play the saved audio file using pygame
                    pygame.mixer.music.load(response_filename)
                    pygame.mixer.music.play()

                    # Display the response text on the screen
                    screen.fill(WHITE)
                    draw_text("Response: " + text, GREEN, screen, width // 2, height // 2)
                    pygame.display.flip()

                    # Wait until the sound finishes playing
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)

                else:
                    print("Empty response from GPT-3.5.")
                    screen.fill(WHITE)
                    draw_text("Error: No response from GPT-3.5", RED, screen, width // 2, height // 2)
                    pygame.display.flip()

            elif "stop" in said.lower():
                print("Stopping the loop.")
                return None

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


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    result = get_audio()
    if result is None:
        running = False

    time.sleep(1)  # Add a delay to avoid rapid looping

pygame.quit()
