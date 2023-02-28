import speech_recognition as sr
import pyttsx3 as tts
import openai
import tkinter as tk
import sys
import os
import threading
from dotenv import load_dotenv
from neuralintents import GenericAssistant

load_dotenv()
openai.api_key = os.getenv("OPEN_API_KEY")


class Assistant:

    def __init__(self) -> None:

        self.recognizer = sr.Recognizer()
        self.speaker = tts.init()
        voices = self.speaker.getProperty("voices")
        self.speaker.setProperty('voice', voices[1].id)
        
        self.assistant = GenericAssistant("intents.json", intent_methods={"ChatGPT": self.ask_anything})
        self.assistant.train_model()

        self.root = tk.Tk()
        self.label = tk.Label(text="👾", font=("Arial", 120))
        self.label.config(fg="purple")
        self.label.pack()

        threading.Thread(target=self.run_assistant).start()

        self.root.mainloop()


    def run_assistant(self) -> None:
        while True:
            try:
                with sr.Microphone(device_index=1) as mic:
                    self.recognizer.adjust_for_ambient_noise(mic, duration=0.3)
                    audio = self.recognizer.listen(mic)

                    text = self.recognizer.recognize_google(audio)
                    text = text.lower()

                    if "hey luna" in text:
                        self.label.config(fg="red")
                        audio = self.recognizer.listen(mic)
                        text = self.recognizer.recognize_google(audio)
                        text = text.lower()

                        if text == "see you later":
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
                            
                            self.label.config(fg="purple")
            except Exception as e:
                print(e)
                self.label.config(fg="purple")
                continue
    

    def ask_anything(self) -> None:

        conversation = ""
        username = "Avi"
        bot_name = "Bravobot"

        while True:
            try:
                self.label.config(fg="green")
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
                    self.label.config(fg="purple")
                    break
            
            except:
                continue
        


if __name__=="__main__":
    Assistant()