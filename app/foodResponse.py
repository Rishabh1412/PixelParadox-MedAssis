from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
import io

# Load environment variables
load_dotenv()  

# Configure the Google Generative AI API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(user_input, image, food_list, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare inputs for the model
        inputs = []
        if user_input:
            inputs.append(user_input)
        if image:
            inputs.extend(image)
        if food_list:
            inputs.append(food_list)
        
        # Add the prompt at the end
        inputs.append(prompt)
        
        # Debugging: Print inputs
        print("Inputs for model:", inputs)
        
        # Generate response from the model
        response = model.generate_content(inputs)
        print(response.text)
        return response.text
    
    except Exception as e:
        print(f"Error in get_gemini_response: {e}")
        return "An error occurred while generating the response."

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            # Read the file data
            bytes_data = uploaded_file.read()
            
            # Create image parts
            image_parts = [
                {
                    "mime_type": "image/jpeg",  # Ensure this matches the image format
                    "data": bytes_data
                }
            ]
            return image_parts
        
        except Exception as e:
            print(f"Error in input_image_setup: {e}")
            return None
    else:
        return None

def check_food_safety(user_input, uploaded_file, input_type, disease):
    # Construct the prompt for the model
    prompt = f"""
    Analyze the provided food items (or single item) and determine if each is safe for a person with {disease}. Provide a brief list with:
    1. Food Item - Safe/Not Safe
    Why: Brief explanation.
    2. Another Food Item (if any else avoid writing further) - Safe/Not Safe
    Why: Brief explanation.

    Conclusion: Safe/Not Safe for {disease}
    """

    try:
        if input_type == "Text Prompt" and user_input:
            food_list = user_input
            image_data = None
        elif input_type == "Image" and uploaded_file:
            food_list = ""
            image_data = input_image_setup(uploaded_file)
        else:
            raise ValueError("Please provide the required input.")
        
        # Debugging: Print input parameters
        print("user_input:", user_input)
        print("image_data:", image_data)
        print("food_list:", food_list)
        print("prompt:", prompt)
        
        # Generate and return the response
        if food_list or image_data:
            response = get_gemini_response("", image_data, food_list, prompt)
            return response
        else:
            raise ValueError("Please provide the required input.")
    
    except Exception as e:
        print(f"Error in check_food_safety: {e}")
        return "An error occurred while processing the request."
