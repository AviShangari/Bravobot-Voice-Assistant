import speech_recognition as sr
import pyttsx3 as tts
import openai
import tkinter as tk
import sys
import os
import threading
import whisper
import torch
import boto3
import pydub
from pydub import playback
import DetermineIntent
import Summarize
from PIL import ImageTk, Image
from dotenv import load_dotenv
# import YoutubeMusicPlayer


# Load the env variables and assign them to their respective variables
load_dotenv()
openai.api_key = os.getenv("OPEN_API_KEY")
 
# Log into YouTube Music
# YoutubeMusicPlayer.log_in()


class Assistant:

    def __init__(self) -> None:

        # Set-up the microphone and speakers
        self.recognizer = sr.Recognizer()
        self.speaker = tts.init()
        self.voices = self.speaker.getProperty("voices")
        self.speaker.setProperty('voice', self.voices[0].id)
        self.speaker.setProperty('rate', 200)

        # Set-up the Whisper offline transcriber
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model("small", device=device)

        # Set-up the link between the tags in intents.json and their functionality
        self.intent_mapping = {"Summarize": Summarize.summarize}

        # Set-up a variable to store song names for song requests
        self.song = ""

        # Set-up wake words for different modules
        self.gpt_wake = "luna"
        self.bot_wake = "bravo"

        # Initialize tkinter and set canvas size
        self.root = tk.Tk()
        self.root.geometry("400x400")

        # Set Transparency
        self.root.attributes('-alpha', 0.5)

        # Set the frame for tkinter
        self.frame = tk.Frame(self.root, width=400, height=400)
        self.frame.pack()
        self.frame.place(anchor='center', relx=0.5, rely=0.5)

        # Create an object of tkinter ImageTk
        self.img = ImageTk.PhotoImage(Image.open("OFR_Demonic.jpg"))

        # Create a Label Widget to display the text or Image
        self.label = tk.Label(self.frame, image = self.img)
        self.label.pack()

        # Create a seperate thread to listen to the user
        self.thread = threading.Thread(target=self.run_assistant)
        self.thread.start()
        
        self.root.mainloop()

    
    def get_command(self) -> str:
        """
        A function that gets the user command and returns it in the form a string
        """
        with sr.Microphone(device_index=1) as mic:
            self.recognizer.adjust_for_ambient_noise(mic, duration=0.2)
            audio = self.recognizer.listen(mic)

            with open("audio.wav", "wb") as f:
                f.write(audio.get_wav_data())
            
            result = self.model.transcribe("audio.wav")
            text = result["text"]

        print(f'Input: {text}')
        return text
    

    def create_speech(self, text, output_file):
        polly = boto3.client('polly', region_name='ca-central-1')

        response = polly.synthesize_speech(
            Text = text,
            OutputFormat = 'mp3',
            VoiceId = 'Amy',
            Engine = 'neural'
        )

        with open(output_file, 'wb') as f:
            f.write(response['AudioStream'].read())
    

    def play_audio(self, file):
        sound =  pydub.AudioSegment.from_file(file, format='mp3')
        playback.play(sound)


    def speak(self, prompt: str) -> None:
        """
        A function that speaks the provided prompt. \n
        Takes a singular string argument in the form: ```self.speak("How can I assist you today?")```
        """
        self.create_speech(prompt, 'response.mp3')
        self.play_audio('response.mp3')

    
    def get_intent(self, key) -> None:
        """Execute an action based on the intent of the user's message """
        self.intent_mapping[key]()


    def switch_profiles(self, name: str) -> None:
        
        self.label.destroy()
        self.img = ImageTk.PhotoImage(Image.open(name))
        self.label = tk.Label(self.frame, image = self.img)
        self.label.pack()

        if name == "OFR_Girl.jpg":
            self.speaker.setProperty('voice', self.voices[1].id)
        else:
            self.speaker.setProperty('voice', self.voices[0].id)



    def run_assistant(self) -> None:
        """
        Core of the assistant. Waits for user input and then executes commands based on user inputs. \n
        The user input is executed based on the functionality defined in the 'intents.json' file.
        """
        while True:
            try:
                text = self.get_command()
                text = text.lower()

                if self.bot_wake in text:

                    self.speak("What's up?")
                    self.switch_profiles("OFR_Demonic.jpg")
                    self.root.attributes('-alpha', 1)

                    text = self.get_command()
                    text = text.lower()
                    
                    if "bye" in text:
                        self.speak("See you later!")
                        self.speaker.stop()
                        self.root.destroy()
                        # YoutubeMusicPlayer.close()
                        sys.exit()

                    else:
                        if text is not None:
                            self.get_intent(DetermineIntent.get_results(text))
                        
                        self.root.attributes('-alpha', 0.5)
                

                elif self.gpt_wake in text:
                    self.ask_anything()
                    self.switch_profiles(name="OFR_Demonic.jpg")
                    self.root.attributes('-alpha', 0.5)

            except Exception as e:
                print(e)
                self.root.attributes('-alpha', 0.5)
                continue
    

    def ask_anything(self) -> None:
        """
        Uses OpenAPI to answer any general/specific queries.\n
        Works by sending a prompt to 'text'davinci-003 engine' and generates a response to return to the user.
        """
        self.switch_profiles('OFR_Girl.jpg')

        conversation = ""
        username = "Avi"
        bot_name = "GPT"

        self.speak("How can I help you today?")

        while True:
            try:
                self.root.attributes('-alpha', 1)                
                text = self.get_command()
                prompt = username + ":" + text + "\n" + bot_name + ":"
                
                conversation += prompt

                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=conversation,
                    temperature=0.7,
                    max_tokens=256,
                    n=1,
                    stop=None
                )

                response_str = response["choices"][0]["text"].replace("\n", "")
                response_str = response_str.split(username + ":", 1)[0].split(bot_name + ":", 1)[0]
                conversation += response_str
                print(response_str + "\n")

                self.speak(response_str)

                if text.lower() == " thank you." or text.lower == " thank you.":
                    self.root.attributes('-alpha', 0.5)
                    break
            
            except:
                continue

    
    # def play_song(self) -> None:
    #     """
    #     Plays a song of the user's preference.\n
    #     Functionality includes asking user's song choice and playing it using Selenium.
    #     """

    #     # self.speak("What song do you want me to play?")
    #     try:
    #         self.root.attributes('-alpha', 1)                
    #         self.speak("Playing " + self.song)
    #         YoutubeMusicPlayer.play_song(self.song)
    #         self.root.attributes('-alpha', 0.5)
    #     except:
    #         self.root.attributes('-alpha', 0.5)
    
    
    # def pause_music(self) -> None:
    #     """
    #     This function pauses/resumes a song.
    #     """
    #     YoutubeMusicPlayer.pause()

    
    def identify_music_request(self, text: str) -> bool:
        """
        Identifies if the voice command is a music request or not.
        """

        if "play" in text.lower() and "song" in text.lower():
            return True
        return False



if __name__=="__main__":
    Assistant()
    # YoutubeMusicPlayer.close()
    print("\n Voice Assistant Terminated")