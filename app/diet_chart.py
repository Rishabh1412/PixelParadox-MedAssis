import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, prompt])
    return response.text

def generate_diet_chart(age, weight, height, disease, allergy, preference, region):
    formatted_input = ", ".join(map(str, [age, weight, height, disease, allergy, preference, region]))

    input_prompts = f"""
    Provide a proper diet chart for 
    1. Breakfast
    2. Lunch
    3. Evening Snacks
    4. Dinner
    in a tabular format with quantities and calories needed for a person with
    age: {age}, weight: {weight} kg, height: {height} metres, preference: {preference} 
    for disease: {disease} containing food dishes from {region} region.
    Avoid the foods with allergies {allergy}.

    after the chart, Also provide a list of food items the user should avoid to eat for the next few weeks.
    Also provide any exercise if needed and a conclusion of the diet chart.
    
    Be very specific and don't provide anything else.
    """
    
    response = get_gemini_response(formatted_input, input_prompts)
    return response

# Streamlit app code
def diet_checker_app():
    st.set_page_config(page_title="Diet Checker")
    st.header("Diet Checker")

    age = st.number_input("Enter Age:", key="age")
    weight = st.number_input("Enter Weight:", key="weight")
    height = st.number_input("Enter Height:", key="height")
    disease = st.text_input("Enter disease:", key="disease")
    allergy = st.text_input("Allergy if any:", key="allergy")
    preference = st.text_input("Preference:", key="preference")
    region = st.text_input("Region:", key="region")

    submit = st.button("Check")

    if submit:
        response = generate_diet_chart(age, weight, height, disease, allergy, preference, region)
        st.subheader("RESPONSE:")
        st.write(response)

if __name__ == "__main__":
    diet_checker_app()