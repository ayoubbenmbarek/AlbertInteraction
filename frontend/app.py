"""Model to Diplay Frontrend functionnalities"""
import os
import json
import httpx
import asyncio

from dotenv import load_dotenv
import requests
import streamlit as st


load_dotenv()

st.set_page_config(page_title="Discuter avec Albert", layout="wide")

st.title("Discuter avec Albert")

BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL")
BACKEND_CHAT_COMPLETION_URL = os.getenv("BACKEND_CHAT_COMPLETION_URL")
BACKEND_UPLOAD_URL = os.getenv("BACKEND_UPLOAD_URL")
BACKEND_COLLECTIONS_URL = os.getenv("BACKEND_COLLECTIONS_URL")
BACKEND_MODELS_URL = os.getenv("BACKEND_MODELS_URL")
COMPLETIONS_URL = os.getenv("COMPLETIONS_URL")
BACKEND_TRANSCRIPTION_URL = os.getenv("BACKEND_TRANSCRIPTION_URL")

# Language choices for transcription
LANGUAGES = {
    "Français": "fr",
    "Anglais": "en",
    "Espagnol": "es",
    "Allemand": "de",
    "Italien": "it"
}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.success("Chat history cleared.")

def get_assistant_reply(user_message, model_id):
    """Send message to Albert Api and get the assistant's reply."""
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message, "name": "Ayoub"}
        ],
        "model": model_id
    }
    try:
        response = requests.post(FASTAPI_CHAT_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Response from backend:", data)  # Log full response for debugging
            assistant_reply = data.get("assistant_reply", "")
            if assistant_reply:
                return assistant_reply
            else:
                st.error("Empty response from assistant.")
                return None
        else:
            st.error(f"Error: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {str(e)}")
        return None


def transcribe_audio(file, language, temperature=0, prompt=""):
    """Send audio file to the backend for transcription."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        data = {
            "model": "openai/whisper-large-v3",
            "language": language,
            "prompt": prompt,
            "response_format": "json",
            "temperature": temperature
        }
        response = requests.post(BACKEND_TRANSCRIPTION_URL, files=files, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error: {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


# def send_message_to_backend(messages, model, temperature, max_tokens, top_p, n, logprobs, 
#                             frequency_penalty, presence_penalty, best_of, echo, logit_bias, stop, 
#                             stream, suffix, user):
#     # Create the payload for the API request, ensuring only valid fields
#     payload = {
#         "messages": [{"role": msg['role'], "content": msg['content'], "name": msg['name']} for msg in messages],  # Include 'name'
#         "model": model,
#         "temperature": temperature,
#         "max_tokens": max_tokens,
#         "top_p": top_p,
#         "n": n,
#         "logprobs": logprobs,
#         "frequency_penalty": frequency_penalty,
#         "presence_penalty": presence_penalty,
#         "best_of": best_of,
#         "echo": echo,
#         "logit_bias": logit_bias,
#         "stop": stop,
#         "stream": stream,
#         "suffix": suffix,
#         "user": user
#     }

#     try:
#         response = requests.post(BACKEND_CHAT_COMPLETION_URL, json=payload)
#         response.raise_for_status()  # Raises HTTPError for bad responses
#         response_data = response.json()
#         return response_data.get("response", "")
#     except requests.exceptions.HTTPError as e:
#         return {"error": f"HTTP Error: {e.response.text}"}
#     except requests.exceptions.RequestException as e:
#         return {"error": f"Request failed: {str(e)}"}

def send_message_to_backend(messages, model, **params):
    payload = {"messages": messages, "model": model, **params}
    try:
        response = requests.post(BACKEND_CHAT_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error: {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}



def send_message(prompt, model_id, **additional_params):
    """Send message to Albert API and retrieve completion."""
    payload = {
        "prompt": prompt,
        "model": model_id,
        **additional_params
    }

    try:
        response = requests.post(COMPLETIONS_URL, json=payload)
        response.raise_for_status()
        response_data = response.json()
        return response_data['choices'][0]['text']
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error: {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


def get_collections():
    """Get collections.

    Returns:
        _type_: _description_
    """
    try:
        response = requests.get(BACKEND_COLLECTIONS_URL)
        response.raise_for_status()
        data = response.json()

        collections = data.get("data", [])

        formatted_collections = []
        for collection in collections:
            formatted_collections.append({
                "id": collection.get("id"),
                "name": collection.get("name"),
                "description": collection.get("description", None),
            })

        return formatted_collections

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des collections : {e}")
        return []


def get_models():
    """_summary_

    Returns:
        _type_: _description_
    """
    try:
        response = requests.get(BACKEND_MODELS_URL)
        response.raise_for_status()
        data = response.json()

        models = data.get("data", [])

        formatted_models = []
        for model in models:
            formatted_models.append({
                "id": model.get("id"),
                "owned_by": model.get("owned_by"),
                "type": model.get("type"),
            })

        return formatted_models

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des modeles : {e}")
        return []


def upload_file(file, collection_id, chunk_size=512, chunk_overlap=0):
    """
    Synchronous version of the upload function using requests.
    """
    try:
        file_data = file.read()

        files = {
            "file": (file.name, file_data, file.type)
        }
        data = {
            "collection": str(collection_id),
            "chunk_size": str(chunk_size),
            "chunk_overlap": str(chunk_overlap),
            "length_function": "len",
            "is_separator_regex": "false",
            "separators": "\n\n,\n,. , ",
            "chunk_min_size": "1",
        }

        response = requests.post(BACKEND_UPLOAD_URL, files=files, data=data)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()

    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error: {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

st.sidebar.title("Fonctionnalités")
option = st.sidebar.selectbox("Choisissez une action :", ["Discuter",
                                                          "Charger un fichier",
                                                          "Voir les collections",
                                                          "Voir les modèles",
                                                          "Transcrire un audio",
                                                          "Assistant"])
# if option == "Assistant":
#     st.subheader("Demande d'assistance")

#     # Get models and model selection
#     models = get_models()
#     model_names = [f"{modell['id']}" for modell in models]
#     selected_model = st.selectbox("Choisissez un modèle", model_names)
#     model = models[model_names.index(selected_model)].get("id")

#     # Get parameters for the model
#     temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
#     max_tokens = st.number_input("Max Tokens", min_value=1, max_value=1024, value=256)
#     top_p = st.slider("Top P", 0.0, 1.0, 1.0)
#     n = st.number_input("Number of Results", min_value=1, max_value=5, value=1)
#     logprobs = st.number_input("Logprobs", min_value=0, value=0)
#     frequency_penalty = st.number_input("Frequency Penalty", min_value=0.0, value=0.0)
#     presence_penalty = st.number_input("Presence Penalty", min_value=0.0, value=0.0)
#     best_of = st.number_input("Best of", min_value=1, value=1)
#     echo = st.checkbox("Echo", value=False)
#     logit_bias = {}  # You can add logit bias here if needed
#     stop = st.text_input("Stop Sequences", value="")
#     stream = st.checkbox("Stream", value=False)
#     suffix = st.text_input("Suffix", value="")
#     user = st.text_input("User", value="user")

#     # Initialize chat history in session state if it doesn't exist
#     if 'chat_history' not in st.session_state:
#         st.session_state.chat_history = []

#     # Input field for user's message
#     user_message = st.text_input("Vous :", placeholder="Écrivez votre message ici...", key="user_message_input")

#     if user_message:
#         # Append user message with 'user' role and include 'name' field
#         st.session_state.chat_history.append({
#             "role": "user",
#             "content": user_message,
#             "name": "user"  # You can customize the name, e.g., user_id
#         })

#         # Send the user message to the backend and get the response
#         assistant_reply = send_message_to_backend(
#             messages=st.session_state.chat_history,
#             model=model,
#             temperature=temperature,
#             max_tokens=max_tokens,
#             top_p=top_p,
#             n=n,
#             logprobs=logprobs,
#             frequency_penalty=frequency_penalty,
#             presence_penalty=presence_penalty,
#             best_of=best_of,
#             echo=echo,
#             logit_bias=logit_bias,
#             stop=stop,
#             stream=stream,
#             suffix=suffix,
#             user=user
#         )

#         # Append assistant's response to chat history with the same 'name' field
#         st.session_state.chat_history.append({
#             "role": "assistant",
#             "content": assistant_reply,
#             "name": "assistant"  # Similarly, use 'assistant' here
#         })

#         # Display the assistant's response
#         st.write(f"Assistant: {assistant_reply}")
if option == "Assistant":
    st.subheader("Demande d'assistance")
    models = get_models()
    model_names = [model['id'] for model in models]
    selected_model = st.selectbox("Choisissez un modèle", model_names)
    model = selected_model

    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    max_tokens = st.number_input("Max Tokens", min_value=1, max_value=1024, value=256)
    top_p = st.slider("Top P", 0.0, 1.0, 1.0)
    n = st.number_input("Number of Results", min_value=1, max_value=5, value=1)
    stop = st.text_input("Stop Sequences", value="string")
    stream = st.checkbox("Stream", value=False)

    user_message = st.text_input("Vous :", placeholder="Écrivez votre message ici...")

    if user_message:
        st.session_state.chat_history.append({"role": "user", "content": user_message, "name": "Ayoub"})
        assistant_reply = get_assistant_reply(user_message, model)  # Pass the user message here
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply, "name": "assistant"})
        st.write(f"Assistant: {assistant_reply}")


# elif option == "Discuter":
#     st.subheader("Discuter avec Albert")

#     models = get_models()
#     model_names = [f"{model['id']}" for model in models]
#     selected_model = st.selectbox("Choisissez un modèle", model_names)
#     selected_model_id = models[model_names.index(selected_model)].get("id")

#     st.subheader("Paramètres de génération")
#     temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
#     max_tokens = st.number_input("Max Tokens", min_value=1, max_value=1024, value=16)
#     top_p = st.slider("Top P", 0.0, 1.0, 0.5)
#     n = st.number_input("Number of Results", min_value=1, max_value=5, value=1)
#     logprobs = st.number_input("Logprobs", min_value=0, value=0)
#     frequency_penalty = st.number_input("Frequency Penalty", min_value=0.0, value=0.0)
#     presence_penalty = st.number_input("Presence Penalty", min_value=0.0, value=0.0)
#     best_of = st.number_input("Best of", min_value=0, value=0)
#     echo = st.checkbox("Echo", value=False)

#     logit_bias = {
#         str(st.number_input("Logit Bias ID 1", value=1234)): st.number_input("Logit Bias Value 1", value=10),
#         str(st.number_input("Logit Bias ID 2", value=5678)): st.number_input("Logit Bias Value 2", value=-5),
#         str(st.number_input("Logit Bias ID 3", value=9012)): st.number_input("Logit Bias Value 3", value=-15),
#     }

#     seed = 0
#     stop = st.text_input("Stop Sequences", value="string")
#     stream = st.checkbox("Stream", value=False)
#     suffix = "string"
#     user = "string"

#     user_message = st.text_input("Vous :", placeholder="Écrivez votre message ici...", key="user_message_input")

#     if user_message:
#         additional_params = {
#             "temperature": temperature,
#             "max_tokens": max_tokens,
#             "top_p": top_p,
#             "n": n,
#             "logprobs": logprobs,
#             "frequency_penalty": frequency_penalty,
#             "presence_penalty": presence_penalty,
#             "best_of": best_of,
#             "echo": echo,
#             "logit_bias": logit_bias,
#             "seed": seed,
#             "stop": stop,
#             "stream": stream,
#             "suffix": suffix,
#             "user": user
#         }

#         albert_response = send_message(user_message, selected_model_id, **additional_params)
#         st.session_state.chat_history.append(("Vous", user_message))
#         st.session_state.chat_history.append(("Albert", albert_response))

#     for sender, message in st.session_state.chat_history:
#         st.markdown(f"**{sender} :** {message}")


elif option == "Charger un fichier":
    st.subheader("Charger un fichier pour le traiter")

    collections = get_collections()
    collection_names = [f"{col['id']} - {col['name']}" for col in collections]
    selected_collection = st.selectbox("Choisissez une collection", collection_names)
    selected_collection_id = collections[collection_names.index(selected_collection)]["id"]

    file = st.file_uploader("Choisissez un fichier", type=["json", "txt"])

    chunk_size = st.number_input("Taille des fragments", value=512, min_value=1)
    chunk_overlap = st.number_input("Chunk Overlap", value=0, min_value=0)

    if file and selected_collection_id and st.button("Charger"):
        upload_response = upload_file(file, selected_collection_id, chunk_size, chunk_overlap)
        if upload_response:
            st.success("Fichier chargé avec succès !")
            st.json(upload_response)

elif option == "Voir les collections":
    st.subheader("Collections disponibles")
    all_collections = get_collections()
    if all_collections:
        for collection in all_collections:
            st.markdown(f"- **ID**: {collection['id']}, **Name**: {collection['name']}, **Description**: {collection.get('description', 'Aucune description')}")

elif option == "Voir les modèles":
    st.subheader("Modèles disponibles")
    all_models = get_models()
    if all_models:
        for model in all_models:
            st.markdown(f"- **ID**: {model['id']}, **Owner**: {model['owned_by']}, **Type**: {model.get('type')}")

if option == "Transcrire un audio":
    st.subheader("Transcription audio")

    audio_file = st.file_uploader("Choisissez un fichier audio", type=["wav", "mp3", "m4a"])
    selected_language = st.selectbox("Choisissez la langue", list(LANGUAGES.keys()))
    temperature = st.slider("Temperature", 0.0, 1.0, 0.5)

    if audio_file and st.button("Transcrire"):
        transcription_result = transcribe_audio(audio_file, LANGUAGES[selected_language])
        if transcription_result:
            st.success("Transcription réussie !")
            st.json(transcription_result)
