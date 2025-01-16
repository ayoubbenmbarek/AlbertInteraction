import streamlit as st
import requests

st.set_page_config(page_title="Discuter avec Albert", layout="wide")

st.title("Discuter avec Albert")

BACKEND_CHAT_URL = "http://127.0.0.1:8000/chat-completion"
BACKEND_UPLOAD_URL = "http://127.0.0.1:8000/upload"
BACKEND_COLLECTIONS_URL = "http://127.0.0.1:8000/collections"
BACKEND_MODELS_URL = "http://127.0.0.1:8000/models"
COMPLETIONS_URL = "http://127.0.0.1:8000/completions"

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# def send_message(msg):
#     """Discuss with Albert.

#     Args:
#         msg (_type_): _description_

#     Returns:
#         _type_: _description_
#     """
#     try:
#         response = requests.post(BACKEND_CHAT_URL, json={"message": msg})
#         response.raise_for_status()
#         data = response.json()
#         return data.get("response", "Albert n'a pas répondu.")
#     except requests.exceptions.RequestException as e:
#         return f"Erreur lors de la connexion au backend : {e}"
def send_message(prompt, model_id, **additional_params):
    """Send message to backend API and retrieve completion."""
    payload = {
        "prompt": prompt,
        "model": model_id,
        **additional_params
    }

    try:
        response = requests.post(COMPLETIONS_URL, json=payload)
        response.raise_for_status()
        # Extract the 'text' field from the response and return it
        response_data = response.json()
        return response_data['choices'][0]['text']  # Extract only the text
    except requests.exceptions.RequestException as e:
        return f"Erreur lors de la connexion au backend : {e}"

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


def upload_file(file, chunk_size=512, chunk_overlap=0):
    """_summary_

    Args:
        file (_type_): _description_
        chunk_size (int, optional): _description_. Defaults to 512.
        chunk_overlap (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        data = {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "length_function": "len",
            "is_separator_regex": "false",
            "separators": "\n\n,\n,. , ",
            "chunk_min_size": 0,
        }
        response = requests.post(BACKEND_UPLOAD_URL, files=files, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        return None


st.sidebar.title("Fonctionnalités")
option = st.sidebar.selectbox("Choisissez une action :", ["Discuter", "Charger un fichier", "Voir les collections", "Voir les modèles"])

# if option == "Discuter":
#     user_message = st.text_input("Vous :", placeholder="Écrivez votre message ici...", key="user_message_input")

#     if user_message:
#         albert_response = send_message(user_message)
#         st.session_state.chat_history.append(("Vous", user_message))
#         st.session_state.chat_history.append(("Albert", albert_response))

#     for sender, message in st.session_state.chat_history:
#         if sender == "Vous":
#             st.markdown(f"**Vous :** {message}")
#         else:
#             st.markdown(f"**Albert :** {message}")
if option == "Discuter":
    st.subheader("Discuter avec Albert")

    models = get_models()
    model_names = [f"{model['owned_by']} - {model['type']}" for model in models]
    model_names = [f"{model['id']}" for model in models]
    selected_model = st.selectbox("Choisissez un modèle", model_names)

    selected_model_id = models[model_names.index(selected_model)].get("id")

    user_message = st.text_input("Vous :", placeholder="Écrivez votre message ici...", key="user_message_input")

    if user_message:
        additional_params = {
            "temperature": st.slider("Temperature", 0.0, 1.0, 1.0),
            "max_tokens": st.number_input("Max Tokens", min_value=1, max_value=1024, value=16),
            "top_p": st.slider("Top P", 0.0, 1.0, 1.0),
            "n": st.number_input("Number of Results", min_value=1, max_value=5, value=1),
            "logprobs": st.number_input("Logprobs", min_value=0, value=0),
            "frequency_penalty": st.number_input("Frequency Penalty", min_value=0.0, value=0.0),
            "presence_penalty": st.number_input("Presence Penalty", min_value=0.0, value=0.0),
            "best_of": st.number_input("Best of", min_value=0, value=0),
            "echo": st.checkbox("Echo", value=False),
            "logit_bias": {
                str(st.number_input("Logit Bias ID 1", value=1234)): st.number_input("Logit Bias Value 1", value=10),
                str(st.number_input("Logit Bias ID 2", value=5678)): st.number_input("Logit Bias Value 2", value=-5)
            },
            "seed": 0,
            "stop": st.text_input("Stop Sequences", value="string"),
            "stream": st.checkbox("Stream", value=False),
            "suffix": "string",
            "user": "string"
        }

        albert_response = send_message(user_message, selected_model_id, **additional_params)
        st.session_state.chat_history.append(("Vous", user_message))
        st.session_state.chat_history.append(("Albert", albert_response))

    for sender, message in st.session_state.chat_history:
        if sender == "Vous":
            st.markdown(f"**Vous :** {message}")
        else:
            st.markdown(f"**Albert :** {message}")

elif option == "Charger un fichier":
    st.subheader("Charger un fichier pour le traiter")
    file = st.file_uploader("Choisissez un fichier", type=["json", "txt"])
    chunk_size = st.number_input("Taille des fragments", value=512, min_value=1)
    chunk_overlap = st.number_input("Chunk Overlap", value=0, min_value=0)

    if file and st.button("Charger"):
        upload_response = upload_file(file, chunk_size, chunk_overlap)
        if upload_response:
            st.success("Fichier chargé avec succès !")
            st.json(upload_response)

elif option == "Voir les collections":
    st.subheader("Collections disponibles")
    all_collections = get_collections()
    if all_collections:
        for collection in all_collections:
            # Display id, name, and description for each collection
            st.markdown(f"- **ID**: {collection['id']}, **Name**: {collection['name']}, **Description**: {collection.get('description', 'Aucune description')}")

elif option == "Voir les modèles":
    st.subheader("Modèles disponibles")
    all_models = get_models()
    if all_models:
        for model in all_models:
            # Display id, name, and description for each collection
            st.markdown(f"- **ID**: {model['id']}, **Owner**: {model['owned_by']}, **Type**: {model.get('type')}")
