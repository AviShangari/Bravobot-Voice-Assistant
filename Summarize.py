from pytesseract import pytesseract
import pyautogui as pai
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPEN_API_KEY")

def summarize():
    path = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    pytesseract.tesseract_cmd = path

    pai.screenshot("summary.png")


    summary_cmd = "Can you summarize and explain this to me in simple terms: \n"
    text = pytesseract.image_to_string("summary.png")
    text = summary_cmd + text

    response = openai.Completion.create(
                model="text-davinci-003",
                prompt=text,
                temperature=0.7,
                max_tokens=1024,
                n=1,
                stop=None
                )
    
    response_str = response["choices"][0]["text"]
    print(response_str)

summarize()