from dotenv import load_dotenv
import os
import time
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def getResponse(prompt, retries=3, delay=2):
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])

    if "model" in prompt.lower() or "assistance" in prompt.lower():
        return "I am your dedicated medical assistant within the Medassis application, here to help with your health-related inquiries."

    prompt = f"You are a knowledgeable and friendly doctor. Respond to the following query in a short, small but clever, helpful and conversational manner as the steps to be taken to solve the issue if any : '{prompt}"

    while retries > 0:
        try:
            response = chat.send_message(prompt, stream=True)
            
            full_response = ""
            
            for chunk in response:
                if hasattr(chunk, 'text'):
                    full_response += chunk.text
                else:
                    print("The response chunk did not contain text.")
            
            if not full_response.strip():
                print("The response did not contain any valid text.")
                return "Sorry, I couldn't process that response."
            
            return full_response.strip()
        
        except Exception as e:
            retries -= 1
            print(f"An error occurred while processing the response: {e}. Retrying...")
            time.sleep(delay)
    
    return "Sorry, I couldn't process that response."

