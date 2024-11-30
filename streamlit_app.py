import streamlit as st
from openai import OpenAI

# Define the classify_comment function before calling it
def classify_comment(comment, category, client):
    if not client:
        return "No client initialized", False, False
    
    prompt = (
        f"As a TikTok comment classifier, classify the comment as 'good' or 'bad'. "
        f"Comment: '{comment}'\n\n"
        "Classification and Reason:"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    classification_and_reason = response.choices[0].message.content.strip()
    is_bad = "bad" in classification_and_reason.lower()
    related_to_category = True
    return classification_and_reason, is_bad, related_to_category

# Initialize session state variables
if "archive_mode" not in st.session_state:
    st.session_state["archive_mode"] = "Archive ALL bad comments"

def main_page(client):
    st.title("📸 Social Media Post")
    
    st.write("Upload a picture to simulate a social media post.")
    uploaded_image = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])
    
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Social Media Post")
        st.write(f"Current Archiving Mode: {st.session_state['archive_mode']}")
        st.write("Generating comments...")
        
        comments = ["Great post!", "Your makeup looks terrible."]
        
        for comment in comments:
            if client:
                classification, is_bad, _ = classify_comment(comment, "general", client)
                if st.session_state["archive_mode"] == "Archive ALL bad comments" and is_bad:
                    st.error(f"🚫 Comment Archived: {comment}")
                else:
                    st.success(f"✅ Comment Kept: {comment}")
            else:
                st.warning("No OpenAI client available.")

def settings_page():
    st.title("⚙️ Settings")
    st.write("Modify your app settings here.")
    
    archive_mode = st.radio(
        "Select your archiving preference:",
        ["Archive ALL bad comments", "Keep ALL Comments", "Customize"],
        index=["Archive ALL bad comments", "Keep ALL Comments", "Customize"].index(st.session_state["archive_mode"]),
    )
    
    # Update session state
    st.session_state["archive_mode"] = archive_mode
    
    st.write(f"Current selection: {st.session_state['archive_mode']}")
    st.info("Return to the main page to see how settings are applied.")

# Page navigation using sidebar
page = st.sidebar.selectbox("Navigate", ["Home", "Settings"])

# OpenAI API Key Section
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
client = None
if openai_api_key:
    try:
        client = OpenAI(api_key=openai_api_key)
    except Exception as e:
        st.sidebar.error(f"Error initializing OpenAI client: {e}")

if page == "Home":
    main_page(client)
elif page == "Settings":
    settings_page()
