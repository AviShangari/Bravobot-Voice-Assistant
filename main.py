import speech_recognition as sr
import pyttsx3 as tts
import openai
import tkinter as tk
import sys
import os
import threading
from PIL import ImageTk, Image
from dotenv import load_dotenv
from neuralintents import GenericAssistant

load_dotenv()
openai.api_key = os.getenv("OPEN_API_KEY")


class Assistant:

    def __init__(self) -> None:

        # Set-up the microphone and speakers
        self.recognizer = sr.Recognizer()
        self.speaker = tts.init()
        voices = self.speaker.getProperty("voices")
        self.speaker.setProperty('voice', voices[0].id)
        self.speaker.setProperty('rate', 200)

        # Initialize and train the Voice Assistant Model with 'Intents'
        self.assistant = GenericAssistant("intents.json", intent_methods={"ChatGPT": self.ask_anything, "Music": self.play_song})
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


    def run_assistant(self) -> None:
        while True:
            try:
                with sr.Microphone(device_index=1) as mic:
                    self.recognizer.adjust_for_ambient_noise(mic, duration=0.3)
                    audio = self.recognizer.listen(mic)

                    text = self.recognizer.recognize_google(audio)
                    text = text.lower()

                    if "bravo" in text:
                        self.root.attributes('-alpha', 1)
                        self.speaker.say("Yes?")
                        self.speaker.runAndWait()
                        self.recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                        audio = self.recognizer.listen(mic)
                        text = self.recognizer.recognize_google(audio)
                        text = text.lower()

                        if text == "bye":
                            self.speaker.say("See you later!")
                            self.speaker.runAndWait()
                            self.speaker.stop()
                            self.root.destroy()
                            sys.exit()

                        else:
                            if text is not None:
                                response = self.assistant.request(text)
                                
                                if response is not None:
                                    self.speaker.say(response)
                                    self.speaker.runAndWait()
                            
                            self.root.attributes('-alpha', 0.5)
            except Exception as e:
                print(e)
                self.root.attributes('-alpha', 0.5)
                continue
    

    def ask_anything(self) -> None:

        conversation = ""
        username = "Avi"
        bot_name = "BravoBot"

        self.speaker.say("Activating Query Mode. How can I help you today?")
        self.speaker.runAndWait()

        while True:
            try:
                self.root.attributes('-alpha', 1)
                with sr.Microphone(device_index=1) as mic:
                    self.recognizer.adjust_for_ambient_noise(mic, duration=0.3)
                    audio = self.recognizer.listen(mic)

                
                text = self.recognizer.recognize_google(audio)
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

                self.speaker.say(response_str)
                self.speaker.runAndWait()

                if text.lower() == 'thank you':
                    self.root.attributes('-alpha', 0.5)
                    break
            
            except:
                continue
        
    
    def play_song(self):
        
        self.speaker.say("What song do you want me to play?")
        self.speaker.runAndWait()


if __name__=="__main__":
    Assistant()
    print("\n Voice Assistant Terminated")