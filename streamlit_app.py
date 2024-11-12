import streamlit as st
from openai import OpenAI
import json
import random
import time
from utils.fix_json import fix_json
from utils.get_assets import get_assets
from utils.file_utils import read_file
from utils.git_utils import GitHubPRCreator

with open("config.json", "r") as config_file:
    config = json.load(config_file)
# Function to get the initial prompt for classifying the error
def get_classify_error_prompt():
    return read_file('prompts/classify_error_prompt.txt')

# Function to get the initial prompt for creation of ticket based on the error
def get_prepare_ticket_for_error_prompt():
    return read_file('prompts/create_ticket_prompt.txt')

# Function to get the error details
def get_data_error_details():
    return read_file('error_samples/demo_error_1.txt')

# Function to make a query to LLM
def ask_llm(messages): 
    return client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0,
            seed=42
        )

# Function to fetch LLM response message content
def get_llm_message_response_content(response):
    return response.choices[0].message.content

# LLM action Function to handle additional context retrieval
def retrieve_additional_context_action(initial_messages, initial_response):
    additional_information = get_assets()
    if additional_information:
        updated_prompt = f"{initial_messages[0]}\n\n---\n\n{additional_information}"
        updated_messages = [{"role": "user", "content": updated_prompt}]
        updated_response = ask_llm([{"role": "user", "content": updated_prompt}])
        updated_result = get_llm_message_response_content(updated_response)
        st.write(updated_result)
        handle_llm_response(updated_messages, updated_result)

# LLM action function to create jira ticket(LLM should provide us a text that needs to be used in jira ticket, title, text, priority, story points etc.)
def rise_incident_action(initial_messages, initial_response):
### IMPLEMENTED TODO 2: Uladzimir: Action to create jira ticket(LLM should provide us a text that needs to be used in jira ticket, title, text, priority, story points etc.)
    prompt = get_prepare_ticket_for_error_prompt()
    error_contents = get_data_error_details()

    if error_contents and prompt:
        messages = [
            {"role": "user", "content": f"{error_contents} \n\n---\n\n {prompt}"}
        ]

        ### Team question: do we need to include context here for the jira ticket?
        response = ask_llm(messages)

        result = get_llm_message_response_content(response)
        st.write(result)

# LLM action function to propose code change for a developer review
def fix_code_action(initial_messages, initial_response):
### TODO 4: Uladzimir: action for the user interaction when LLM provided git diff, we should request user review and approval or rejection
## TODO switch to session state
    user_input_key = f"fix_code_action-{random.randint(1, 100)}"
    suggested_changes = dict(json.loads(initial_response))
    pr_url = GitHubPRCreator(config["github_token"], config["owner"], config["repo"], config["base_branch"], user_input_key, suggested_changes).create_pr_with_changes()
    st.write(f"Draft PR link: {pr_url}")
    # Ask the user if he approves the modification
    user_answer = any
    user_answer = st.text_input(
        f"Please review the changes proposed to fix the issues (follow the above link). Do you approve this Yes/No?",
        key=user_input_key)
    while not user_answer:
        time.sleep(2.5)
        st.write("DEBUG: No answer")
    # Normalize the input to lower case for case-insensitive comparison
    normalized_answer = user_answer.strip().lower()

    st.write(f"DEBUG: normalized_answer: {normalized_answer}")
    if normalized_answer not in ['yes', 'no']:
        st.write("Reply with Yes or No please")
        fix_code_action(initial_messages, initial_response)
    else:
        approved = normalized_answer == 'yes'
        declined = normalized_answer == 'no'
        if approved:
            st.write("Applying code change to git")
            ## todo change application logic to apply code
        if declined:
            st.write("Code change not applied")
            ## todo think what we should do in such case
    
    st.write("DEBUG: exited fix_code_action")


# def create_pr_action(initial_messages, llm_response)


### TODO 3: Viacheslav: fix json parsing for git diff issues in LLM response

### TODO 5: Stanislau: find configuration parser code

# Function to handle the response from the language model
def handle_llm_response(initial_messages, llm_response):
    try:
        llm_response = fix_json(llm_response)
        parsed_result = json.loads(llm_response)
        issue_level = parsed_result.get("issueLevel")
        st.write(f"Issue level detected is {issue_level}")
        suggested_action = parsed_result.get("suggestedAction")

        # Define supported action handlers
        action_handlers = {
            "request_additional_context": lambda: retrieve_additional_context_action(initial_messages, llm_response),
            "rise_an_incident": lambda: rise_incident_action(initial_messages, llm_response),
            "fix_code": lambda: fix_code_action(initial_messages, llm_response),
            # "create_pr": lambda: create_pr_action(initial_messages, llm_response)
            # Add more actions here
        }

        # Execute the appropriate action based on the suggested action
        handler = action_handlers.get(suggested_action, lambda: st.error(f"The action {suggested_action} is not yet registered."))
        handler()
    except json.JSONDecodeError:
        st.error(f"Failed to parse the response as JSON: {llm_response}")

### Main application

st.title("📄 Data Pipeline Assistant")

# Request the OpenAI API key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client
    client = OpenAI(api_key=openai_api_key)
    # client = openai.AzureOpenAI(api_key=openai_api_key, api_version="2024-08-01-preview", azure_endpoint=st.secrets.aoai.endpoint_full)
    prompt = get_classify_error_prompt()
    error_contents = get_data_error_details()

    if error_contents and prompt:
        messages = [
            {"role": "user", "content": f"{prompt} \n\n---\n\n {error_contents}"}
        ]
        response = ask_llm(messages)

        result = get_llm_message_response_content(response)
        st.write(result)
        handle_llm_response(messages, result)
        st.write("Execution finished")


### Examples for future use:
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