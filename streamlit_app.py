import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
import json
import random
import time
from utils.fix_json import fix_json
from utils.get_assets import get_assets
from utils.file_utils import read_file

# Initialize the OpenAI LLM with LangChain
def initialize_llm(api_key):
    return ChatOpenAI(
        api_key=api_key,
        model="gpt-4o",
        temperature=0,
        seed=42
    )

# Function to load the prompt template for error classification
def load_classify_error_prompt():
    return read_file('prompts/classify_error_prompt.txt')

# Function to load the prompt template for creating a ticket based on the error
def load_prepare_ticket_prompt():
    return read_file('prompts/create_ticket_prompt.txt')

# Function to load the error details
def load_error_details():
    return read_file('error_samples/demo_error_1.txt')

# Function to create LLM query using LangChain
def ask_llm(llm, messages):
    chain = LLMChain(llm=llm, prompt=PromptTemplate(input_variables=['content'], template="{content}"))
    return chain.run(content=messages[0]["content"])

# Retrieve and update context if additional information is available
def retrieve_additional_context_action(llm, initial_messages):
    additional_information = get_assets()
    if additional_information:
        updated_content = f"{initial_messages[0]['content']}\n\n---\n\n{additional_information}"
        updated_messages = [{"role": "user", "content": updated_content}]
        updated_response = ask_llm(llm, updated_messages)
        st.write(updated_response)
        handle_llm_response(llm, updated_messages, updated_response)

# Create Jira ticket from LLM response for an incident
def rise_incident_action(llm, initial_messages):
    prompt = load_prepare_ticket_prompt()
    error_contents = load_error_details()

    if error_contents and prompt:
        messages = [{"role": "user", "content": f"{error_contents} \n\n---\n\n {prompt}"}]
        response = ask_llm(llm, messages)
        st.write(response)

# Propose code change and handle approval for developer review
def fix_code_action(initial_messages, initial_response):
    user_input_key = f"fix_code_action-{random.randint(1, 100)}"
    user_answer = st.text_input("Please review the changes proposed to fix the issues. Do you approve this Yes/No?", key=user_input_key)

    while not user_answer:
        time.sleep(2.5)
        st.write("Waiting for your response...")

    normalized_answer = user_answer.strip().lower()
    if normalized_answer not in ['yes', 'no']:
        st.write("Reply with Yes or No please")
        fix_code_action(initial_messages, initial_response)
    else:
        if normalized_answer == 'yes':
            st.write("Applying code change to git")
            # TODO: Apply code change
        elif normalized_answer == 'no':
            st.write("Code change not applied")

# Handle LLM response and execute appropriate action
def handle_llm_response(llm, initial_messages, llm_response):
    try:
        llm_response = fix_json(llm_response)
        parsed_result = json.loads(llm_response)
        issue_level = parsed_result.get("issueLevel")
        st.write(f"Issue level detected is {issue_level}")
        suggested_action = parsed_result.get("suggestedAction")

        action_handlers = {
            "request_additional_context": lambda: retrieve_additional_context_action(llm, initial_messages),
            "rise_an_incident": lambda: rise_incident_action(llm, initial_messages),
            "fix_code": lambda: fix_code_action(initial_messages, llm_response)
        }

        handler = action_handlers.get(suggested_action, lambda: st.error(f"Unregistered action: {suggested_action}"))
        handler()
    except json.JSONDecodeError:
        st.error(f"Failed to parse response as JSON: {llm_response}")

# Main Application
st.title("📄 Data Pipeline Assistant")

openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    llm = initialize_llm(api_key=openai_api_key)
    prompt = load_classify_error_prompt()
    error_contents = load_error_details()

    if error_contents and prompt:
        messages = [{"role": "user", "content": f"{prompt} \n\n---\n\n {error_contents}"}]
        response = ask_llm(llm, messages)

        st.write(response)
        handle_llm_response(llm, messages, response)
        st.write("Execution finished")