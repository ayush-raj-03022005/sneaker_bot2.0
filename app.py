import streamlit as st
import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set page config with sneaker theme
st.set_page_config(
    page_title="🔥 Ultimate Sneaker Bot",
    page_icon="👟",
    layout="centered"
)

# Set background image
def set_background():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://images4.alphacoders.com/683/thumb-1920-683744.jpg");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.8);
            border-radius: 15px;
            padding: 2rem;
            margin-top: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .stChatMessage {{
            background-color: rgba(20, 20, 20, 0.9) !important;
            border-radius: 15px !important;
            padding: 1.5rem !important;
            margin: 1rem 0 !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
        }}
        .stTextInput input {{
            background-color: rgba(30, 30, 30, 0.9) !important;
            color: white !important;
            border: 1px solid #444 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "👋 Hey sneakerhead! 🔥\n\nAsk me about:\n- 🚀 Upcoming releases\n- 🎟️ Raffle information\n- 🔄 Restock alerts\n- 📅 Release dates\n\nI'm your ultimate sneaker guide! 👟"
    }]

# Configure sidebar
with st.sidebar:
    st.title("⚙️ Bot Settings")
    api_key = st.text_input("🔑 OpenRouter API Key", type="password")
    st.markdown("[Get API Key](https://openrouter.ai/keys)")
    
    # Model selection
    model_name = st.selectbox(
        "🤖 Choose Model",
        ("google/palm-2-chat-bison",),
        index=0
    )
    
    # Advanced settings
    with st.expander("🎛️ Advanced Settings"):
        temperature = st.slider("🎨 Response Creativity", 0.0, 1.0, 0.7)
        max_retries = st.number_input("🔄 Max Retries", 1, 5, 2)
    
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "🧹 Chat cleared! Ask me about the latest sneaker drops! 👟🔥"
        }]

# Main interface
st.title("👟 AI Sneaker Release Tracker")
st.caption("Never miss a drop with real-time updates on limited editions and exclusive releases")
st.caption("Ayush Raj | Shokendra Singh | Marouf Wani")

# Display chat history with enhanced formatting
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Add emoji enhancement to assistant messages
        if message["role"] == "assistant":
            content = message["content"]
            # Replace hyphens with emoji bullets
            content = content.replace("- ", "• ")
            st.markdown(content)
        else:
            st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask about sneakers..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("🔐 API key required! Please enter your OpenRouter key in the sidebar.")
        st.stop()

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        attempts = 0
        
        # Thinking animation
        with st.spinner("🔍 Checking the latest sneaker news..."):
            while attempts < max_retries:
                try:
                    # API request with enhanced emoji formatting
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://sneaker-bot.streamlit.app",
                            "X-Title": "Ultimate Sneaker Bot"
                        },
                        json={
                            "model": model_name,
                            "messages": [
                                {
                                    "role": "system",
                                    "content": f"""You are a professional sneaker release analyst. Follow these rules:
1. Use emojis to make responses engaging
2. Format lists with bullet points (•)
3. Include dates as: Month Day, Year
4. Structure information clearly:
• 🔥 Release Name: [Name]
• 📅 Date: [Date]
• 🏪 Stores: [Where to buy]
• 💰 Resell: [Price]
5. Current date: {time.strftime("%B %d, %Y")}"""
                                },
                                *st.session_state.messages
                            ],
                            "temperature": temperature,
                            "response_format": {"type": "text"}
                        },
                        timeout=15
                    )

                    response.raise_for_status()
                    data = response.json()
                    raw_response = data['choices'][0]['message']['content']
                    
                    # Process response to enhance formatting
                    processed_response = raw_response
                    
                    # Clean response
                    formatting_cleaners = [
                        ("```json", ""), ("```", ""), ("\\boxed{", ""),
                        ("**", ""), ("###", ""), ("####", ""), ("\\n", "\n"),
                        ('"', "'"), ("{", ""), ("}", "")
                    ]
                    
                    for pattern, replacement in formatting_cleaners:
                        processed_response = processed_response.replace(pattern, replacement)
                    
                    # Enhance lists with emojis
                    lines = processed_response.split('\n')
                    enhanced_lines = []
                    for line in lines:
                        if line.startswith("- Release Name:"):
                            line = "🔥 " + line[2:]
                        elif line.startswith("- Date:"):
                            line = "📅 " + line[2:]
                        elif line.startswith("- Stores:"):
                            line = "🏪 " + line[2:]
                        elif line.startswith("- Resell:"):
                            line = "💰 " + line[2:]
                        enhanced_lines.append(line)
                    
                    processed_response = '\n'.join(enhanced_lines)
                    
                    # Stream response
                    for chunk in processed_response.split():
                        full_response += chunk + " "
                        response_placeholder.markdown(full_response + "▌")
                        time.sleep(0.03)
                    
                    response_placeholder.markdown(full_response)
                    break
                    
                except json.JSONDecodeError as e:
                    logging.error(f"JSON Error: {str(e)}")
                    attempts += 1
                    if attempts == max_retries:
                        response_placeholder.error("⚠️ Failed to process response. Try rephrasing")
                        full_response = "🔄 Error: Please try asking differently"
                    else:
                        time.sleep(0.5)
                    
                except requests.exceptions.RequestException as e:
                    response_placeholder.error(f"🌐 Network Error: {str(e)}")
                    full_response = "⚠️ Connection issue - try again later"
                    break
                    
                except Exception as e:
                    logging.error(f"Unexpected Error: {str(e)}")
                    response_placeholder.error(f"❌ Error: {str(e)}")
                    full_response = "😢 Oops! Something went wrong."
                    break

    st.session_state.messages.append({"role": "assistant", "content": full_response})
