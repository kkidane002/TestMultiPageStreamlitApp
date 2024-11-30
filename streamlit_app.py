import streamlit as st
from openai import OpenAI

# Import your custom modules or page functions
def main_page(client):
    st.title("📸 Social Media Post")
    
    st.write("Upload a picture to simulate a social media post.")
    uploaded_image = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])
    
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Social Media Post")
        st.write("Generating comments...")
        
        # Example comments (you could generate these dynamically)
        comments = ["Great post!", "Your makeup looks terrible."]
        
        for comment in comments:
            classification, is_bad, _ = classify_comment(comment, "general", client)
            if is_bad:
                st.error(f"🚫 Comment Archived: {comment}")
            else:
                st.success(f"✅ Comment Kept: {comment}")


def settings_page():
    st.title("⚙️ Settings")
    st.write("Modify your app settings here.")
    
    st.write("Example Setting: Archiving Mode")
    archive_mode = st.radio(
        "Select your archiving preference:",
        ["Archive ALL bad comments", "Keep ALL Comments", "Customize"]
    )
    
    st.write(f"Current selection: {archive_mode}")
    st.info("Return to the main page to see how settings are applied.")


# Page Navigation using a sidebar
page = st.sidebar.selectbox("Navigate", ["Home", "Settings"])

# OpenAI API Key Section (Reusable)
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
else:
    st.sidebar.info("Please enter your OpenAI API key to use the app.", icon="🔑")
    client = None

if page == "Home":
    if client:
        main_page(client)
    else:
        st.warning("Please provide your API key to use the home page.")
elif page == "Settings":
    settings_page()

# Classify comment function remains as previously defined
def classify_comment(comment, category, client):
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
