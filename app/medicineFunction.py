from dotenv import load_dotenv
import os
import google.generativeai as genai
from mimetypes import guess_type

# Load environment variables from .env file
load_dotenv()

# Configure Google Gemini API with the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_medicine_information_from_image(uploaded_file):
    """
    Function to identify medicines from an image and provide detailed, user-friendly information.
    
    Parameters:
    - uploaded_file: Uploaded image file of the medicines.
    
    Returns:
    - str: Response text from the Google Gemini API.
    """
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

    # Prepare inputs for the model based on image input
    image_data = input_image_setup(uploaded_file)
    print("image_data : ", image_data)

    if image_data:
        try:
            # Modify the prompt to ask for user-friendly information
            detailed_prompt = """
            Please identify the medicines shown in the image. For each medicine, provide a detailed but easy-to-understand explanation that includes:
            1. Name of the medicine
            2. What it is used for
            3. When and how to take it
            4. Any important information the user should be aware of
            
            Please explain it as if you were a friendly doctor talking to a patient.
            """
            
            # Initialize the model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Prepare inputs for the model with the prompt and image data
            inputs = []

            inputs.append(detailed_prompt)
            inputs.extend(image_data)
            
            # Generate response from the model
            response = model.generate_content(inputs)
            print(response.text)
            return response.text
        
        except Exception as e:
            return f"An error occurred: {str(e)}"
    else:
        return "Please provide an image input."
