import streamlit as st
import openai
from PIL import Image
import io
import os
from googletrans import Translator

# Load the OpenAI API key securely from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("OpenAI API key not found. Please set it as an environment variable.")
else:
    openai.api_key = openai_api_key  # Set OpenAI API key
    translator = Translator()  # Initialize the Google Translator
    

# Initialize Google Translator
translator = Translator()

# Define the translate_comment function using googletrans
def translate_comment(comment):
    try:
        translated = translator.translate(comment, src='auto', dest='en')  # Automatically detect the language
        return translated.text
    except Exception as e:
        st.error(f"Error occurred while translating: {e}")
        return comment  # Fallback to original comment if error occurs

# Define the classify_comment function using chat-based API
def classify_comment(comment, category):
    # Define the messages as required by the chat-based API
    messages = [
        {"role": "system", "content": "You are a helpful TikTok comment classifier."},
        {"role": "user", "content": f"Classify the following comment as 'good' or 'bad' specifically in relation to '{category}': {comment}"}
    ]
    
    try:
        # Use the chat/completions endpoint
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the chat model
            messages=messages,
            temperature=0.2,
            max_tokens=150
        )
        
        classification_and_reason = response['choices'][0]['message']['content'].strip()
        
        # Determine if the comment is 'bad' or related to the category
        is_bad = "bad" in classification_and_reason.lower()
        related_to_category = "yes" in classification_and_reason.lower().split("is this comment related to the category?")[-1].strip()
        
        return classification_and_reason, is_bad, related_to_category
    
    except Exception as e:
        st.error(f"Error occurred while classifying the comment: {e}")
        return "Error", False, False

# Initialize session state variables
if "archive_mode" not in st.session_state:
    st.session_state["archive_mode"] = "Keep ALL Comments"

if "custom_category" not in st.session_state:
    st.session_state["custom_category"] = "none"

if "uploaded_image" not in st.session_state:
    st.session_state["uploaded_image"] = None

def main_page():
    st.title("📸 KLS Media Post")
    
    uploaded_image = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])

    # Save the uploaded image to session state
    if uploaded_image:
        st.session_state["uploaded_image"] = uploaded_image
    
    # Display the uploaded image if it exists in session state
    if st.session_state["uploaded_image"]:
        image_bytes = st.session_state["uploaded_image"].getvalue()
        image = Image.open(io.BytesIO(image_bytes))
        st.image(image, caption="Uploaded Social Media Post")
        
        st.write(f"Current Archiving Mode: {st.session_state['archive_mode']}")
        if st.session_state["archive_mode"] == "Customize":
            st.write(f"Current Archiving Category: {st.session_state['custom_category']}")
        # Hardcoded comments
        comments = ["Great post!", "Your makeup looks terrible.", "Amazing style!", "You are not in good body shape."]
        
        # User input for custom comments
        custom_comment = st.text_input("Add Comment...")
        if custom_comment:
            comments.append(custom_comment)
        
        for comment in comments:
            # Translate comment if necessary
            translated_comment = translate_comment(comment)

            if st.session_state["archive_mode"] == "Customize":
                category = st.session_state["custom_category"]
                classification, is_bad, related = classify_comment(translated_comment, category)
                if is_bad and related:
                    st.error(f"🚫 Comment Archived: {comment} (Translated: {translated_comment})")
                else:
                    st.success(f"✅ Comment Kept: {comment} (Translated: {translated_comment})")
            
            elif st.session_state["archive_mode"] == "Archive ALL bad comments":
                classification, is_bad, _ = classify_comment(translated_comment, "general")
                if is_bad:
                    st.error(f"🚫 Comment Archived: {comment} (Translated: {translated_comment})")
                else:
                    st.success(f"✅ Comment Kept: {comment} (Translated: {translated_comment})")
            
            elif st.session_state["archive_mode"] == "Keep ALL Comments":
                st.success(f"✅ Comment Kept: {comment} (Translated: {translated_comment})")

def settings_page():
    st.title("⚙️ KLS Media Settings")
    st.write("Modify your KLS app settings here.")
    
    archive_mode = st.radio(
        "Select your archiving preference:",
        ["Archive ALL bad comments", "Keep ALL Comments", "Customize"],
        index=["Archive ALL bad comments", "Keep ALL Comments", "Customize"].index(st.session_state["archive_mode"]),
    )
    
    st.session_state["archive_mode"] = archive_mode
    
    if archive_mode == "Customize":
        category = st.selectbox(
            "Select the type of comments to archive:",
            options=["Body", "Makeup", "Personality", "Fashion", "Performance"],
        ).lower()
        st.session_state["custom_category"] = category
    
    st.write(f"Current selection: {st.session_state['archive_mode']}")
    if archive_mode == "Customize":
        st.write(f"Custom Category: {st.session_state['custom_category']}")
    st.info("Return to the post feed page to see how settings are applied.")

# Page navigation using sidebar
page = st.sidebar.selectbox("Navigate", ["Post Feeds", "Settings"])

if page == "Post Feeds":
    main_page()
elif page == "Settings":
    settings_page()

