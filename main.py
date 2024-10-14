import openai
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import base64

def setup_openai_client(api_key):
    try:
        return openai.OpenAI(api_key=api_key)
    except Exception as e:
        print(f"Error setting up OpenAI client: {e}")   # Handle the error as needed

def transcribe_audio(client, audio_path):
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(model= "whisper-1",file=audio_file)
        return transcript.text
    
def auto_play_audio(audio_file):
    with open(audio_file, 'rb') as audio_file:
        audio_bytes = audio_file.read()
    base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
    audio_html = f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

    
    
def fetch_ai_response(client, input_text):
    messages = [{"role":"user", "content": input_text}]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8)
    return response.choices[0].message.content

def text_to_audio(client,text,audio_path):
    response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=text
)
    response.stream_to_file(audio_path)


def main():
    
    st.sidebar.title("API KEY CONFIGURATION")
    api_key = st.sidebar.text_input("Enter your OpenAI API key",type="password")
    
    st.title("CERSEI - VOICE ASSISTANT")
    st.write("Hello! Click on the Voice Recorder to interact with me.")
    
    if api_key:
        client = setup_openai_client(api_key)
        recorded_audio = audio_recorder()
        
        if recorded_audio:
            audio_file = "audio.mp3"
            with open(audio_file, 'wb') as f:
                f.write(recorded_audio)
            
            transcribed_text = transcribe_audio(client,audio_file)
            st.markdown("<h3 style='margin: 0;'>Audio Transcribed Text</h3>", unsafe_allow_html=True)
            st.markdown(f"<p>{transcribed_text}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            ai_response = fetch_ai_response(client,transcribed_text)
            response_audio_file = "audio_response.mp3"
            
            audio_text = text_to_audio(client,ai_response, response_audio_file)
            # st.audio(response_audio_file)
            auto_play_audio(response_audio_file)
            st.markdown("<h3 style='margin: 0;'>AI Response:</h3>", unsafe_allow_html=True) 
            st.markdown(f"<p>{ai_response}</p>", unsafe_allow_html=True)   
            st.markdown("</div>", unsafe_allow_html=True)
        else:
                st.write("Please record your voice to interact.")
    
    else:
        st.write("Please enter your OpenAI API key in the sidebar.")
    
if __name__ == "__main__":
    main()