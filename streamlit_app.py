import streamlit as st
from openai import OpenAI
import openai
import json

def handleLlmResponse(result):
        try:
            parsed_result = json.loads(result)
            issue_level = parsed_result.get("issueLevel")
            suggested_action = parsed_result.get("suggestedAction")

            if suggested_action == "request_additional_context":
                additional_question = st.text_input("Please provide more context or clarify your question:")
                if additional_question:
                    updated_prompt = f"{prompt}\n\n---\n\n{additional_question}"
                    updated_response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "user", "content": updated_prompt}
                        ]
                    )
                    updated_result = updated_response.choices[0].message.content
                    st.write(updated_result)
        except json.JSONDecodeError:
            st.error("Failed to parse the response as JSON.")

# Show title and description.
st.title("📄 Data pipeline assistant")

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)
    # client = openai.AzureOpenAI(api_key=openai_api_key, api_version="2024-08-01-preview", azure_endpoint=st.secrets.aoai.endpoint_full)

    # Let the user upload a file via `st.file_uploader`.
    # uploaded_file = st.file_uploader(
    #     "Upload a document (.txt or .md)", type=("txt", "md")
    # )

    # # Ask the user for a question via `st.text_area`.
    # question = st.text_area(
    #     "Now ask a question about the document!",
    #     placeholder="Can you give me a short summary?",
    #     disabled=not uploaded_file,
    # )

    with open('demo_error_1.txt', 'r') as file:
        file_contents = file.read()

    prompt = file_contents
    
    with open('init_prompt.txt', 'r') as file:
        file_contents = file.read()

    error_contents = file_contents
    if error_contents and prompt:
        messages = [
            {
                "role": "user",
                "content": f"{error_contents} \n\n---\n\n {prompt}",
            }
        ]

        # Generate an answer using the OpenAI API.
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            stream=False,
        )


        result = response.choices[0].message.content
        st.write(result)
        handleLlmResponse(result)
