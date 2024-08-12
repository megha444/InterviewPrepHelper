import json
import html
import re
import google.generativeai as genai
from flask import Flask,render_template, render_template_string, request, jsonify
import speech_recognition as sr

app = Flask(__name__)

recognizer = sr.Recognizer()

@app.route("/")
def home():
  return render_template("index.html")

with open('keys.json', 'r') as json_file:
    data = json.load(json_file)

# Set your API key here
GEMINI_API_KEY = data.get('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
  "temperature": 0.35,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 1024,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)

#topic = input("Enter a topic to start interview prep on: ")

#print("To end chat at any time, enter 'NO'")

topic = "kubernetes"
chat_session = model.start_chat(history = [
   {
      "role":"user",
      "parts": ["Act as an interviewer looking to ask about a given topic. Ask me questions and evaluate my responses based on the same. Also suggest how to modify my responses to best suit the topic"]
   }
])

#message  = "Act as an interviewer looking to ask about a given topic. Ask me questions and evaluate my responses based on the same. Also suggest how to modify my responses to best suit the topic"

def record_audio():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    return audio

def recognize_speech(audio):
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that.")
    except sr.RequestError:
        print("Sorry, there was an error processing your request.")


def get_message(prompt):
   response = chat_session.send_message(prompt)
   return response.text

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    response = get_message(userText)
    
    def format_to_html(input_string):
        formatted_string = input_string.replace("\n", "<br>")
        formatted_string = re.sub(r'\*(.*?)\*', r'<strong>\1</strong>', formatted_string)
        formatted_string = re.sub(r'\n\s*\*\s*(.*)', r'<li>\1</li>', formatted_string)
        if '<li>' in formatted_string:
            formatted_string = '<ul>' + formatted_string + '</ul>'
        return formatted_string
    
    html_output = format_to_html(response)
    return (html_output)
    
    
if __name__ == "__main__":
  app.run(debug = True)