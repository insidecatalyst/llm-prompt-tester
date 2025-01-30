import streamlit as st
import requests
import os, json
from dotenv import load_dotenv

load_dotenv()

def main():
    openwebui_url = os.getenv('OPEN_WEBUI_BASE_URL') + '/api'
    openwebui_api_key = os.getenv('OPEN_WEBUI_API_KEY')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openwebui_api_key}'
    }

    st.set_option('client.toolbarMode', 'minimal')
    st.set_page_config(
        page_title='LLM Prompt Tester • The Catalyst Studio',
        layout='wide')
    
    st.html('<style> \
            section div.stMainBlockContainer { padding-top: 2rem; } \
            .stHeading h1:first-child { padding-bottom: 2.5rem } \
            </style>')
    st.title('LLM Prompt Tester')

    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        try:
            models_response = requests.get(f"{openwebui_url}/models", headers=headers).json()
            if 'data' not in models_response:
                raise ValueError("Failed to fetch models from OpenWebUI")
            
            available_models = [model['id'] for model in models_response['data']]
            selected_model = st.selectbox("Model", available_models)
        except Exception as e:
            st.error(f"ERROR: {str(e)}\nResponse: {models_response}")
            return
        
        selected_temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.8)
        context_length = st.slider("Context Length", min_value=0, max_value=51200, value=2048)
        
        system_message = st.text_area("System Message", "You are a helpful assistant.", height=300)
        user_prompt = st.text_area("User Prompt", "Hello!", height=300)

        submit_button = st.button("Generate Response")
        

    with col2:
        st.markdown("### Response:")

        if submit_button:
            try:
                payload = {
                    "model": selected_model,
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": selected_temp,
                    "context_length": int(context_length)
                }
                
                response = requests.post(
                    url=f"{openwebui_url}/chat/completions",
                    headers=headers,
                    data=json.dumps(payload)
                )

                print(f'{response.status_code} {response.reason}')
                
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content']
                    
                    st.markdown(content)
                else:
                    st.error(f"API request failed with status code: {response.status_code}")
                    st.markdown(f"Error message: {response.text}")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
if __name__ == "__main__":
    main()
