import speech_recognition as sr
import pyttsx3 as tts
import openai
import tkinter as tk
import sys
import os
import threading
import time
import YoutubeMusicPlayer
from PIL import ImageTk, Image
from dotenv import load_dotenv
from neuralintents import GenericAssistant

# Load the env variables and assign them to their respective variables
load_dotenv()
openai.api_key = os.getenv("OPEN_API_KEY")

# Log into YouTube Music
YoutubeMusicPlayer.log_in()


class Assistant:

    def __init__(self) -> None:

        # Set-up the microphone and speakers
        self.recognizer = sr.Recognizer()
        self.speaker = tts.init()
        voices = self.speaker.getProperty("voices")
        self.speaker.setProperty('voice', voices[0].id)
        self.speaker.setProperty('rate', 200)

        # Set-up the link between the tags in intents.json and their functionality
        self.intent_mapping = {"ChatGPT": self.ask_anything, "Music": self.play_song, "PausePlayMusic": self.pause_music}

        # Initialize and train the Voice Assistant Model with 'Intents'
        self.assistant = GenericAssistant("intents.json", intent_methods=self.intent_mapping)
        self.assistant.train_model()

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
        img = ImageTk.PhotoImage(Image.open("OFR_Demonic.jpg"))

        # Create a Label Widget to display the text or Image
        self.label = tk.Label(self.frame, image = img)
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
            self.recognizer.adjust_for_ambient_noise(mic, duration=0.3)
            audio = self.recognizer.listen(mic)

            
        text = self.recognizer.recognize_google(audio)
        return text
    

    def speak(self, prompt: str) -> None:
        """
        A function that speaks the provided prompt. \n
        Takes a singular string argument in the form: self.speak(prompt: str)
        """
        self.speaker.say(prompt)
        self.speaker.runAndWait()


    def run_assistant(self) -> None:
        """
        Core of the assistant. Waits for user input and then executes commands based on user inputs. \n
        The user input is executed based on the functionality defined in the 'intents.json' file.
        """
        while True:
            try:
                text = self.get_command()
                text = text.lower()

                if "bravo" in text:
                    self.root.attributes('-alpha', 1)
                    self.speak("Yes?")
                    text = self.get_command()
                    text = text.lower()

                    if text == "bye":
                        self.speak("See you later!")
                        self.speaker.stop()
                        self.root.destroy()
                        YoutubeMusicPlayer.close()
                        sys.exit()

                    else:
                        if text is not None:
                            response = self.assistant.request(text)
                            
                            if response is not None:
                                self.speak(response)
                        
                        self.root.attributes('-alpha', 0.5)

            except Exception as e:
                print(e)
                self.root.attributes('-alpha', 0.5)
                continue
    

    def ask_anything(self) -> None:
        """
        Uses OpenAPI to answer any general/specific queries.\n
        Works by sending a prompt to 'text'davinci-003'engine' and generates a response to return to the user.
        """

        conversation = ""
        username = "Avi"
        bot_name = "BravoBot"

        self.speak("Activating Query Mode. How can I help you today?")

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
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )

                response_str = response["choices"][0]["text"].replace("\n", "")
                response_str = response_str.split(username + ":", 1)[0].split(bot_name + ":", 1)[0]
                conversation += response_str
                print(response_str)

                self.speak(response_str)

                if text.lower() == 'thank you':
                    self.root.attributes('-alpha', 0.5)
                    break
            
            except:
                continue
        
    
    def play_song(self) -> None:
        """
        Plays a song of the user's preference.\n
        Functionality includes asking user's song choice and playing it using Selenium.
        """

        self.speak("What song do you want me to play?")
        try:
            self.root.attributes('-alpha', 1)                
            text = self.get_command()
            self.speak("Playing " + text)
            YoutubeMusicPlayer.play_song(text)
            self.root.attributes('-alpha, 0.5')
        except:
            self.root.attributes('-alpha', 0.5)
    
    
    def pause_music(self) -> None:
        """
        This function pauses/resumes a song.
        """
        YoutubeMusicPlayer.pause()



if __name__=="__main__":
    Assistant()
    print("\n Voice Assistant Terminated")