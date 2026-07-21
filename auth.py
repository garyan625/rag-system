import streamlit as st
import firebase_admin

from firebase_admin import (
    credentials,
    firestore,
    auth as firebase_auth
)

from streamlit_oauth import OAuth2Component

# ==========================================
# FIREBASE ADMIN INITIALIZATION
# ==========================================

if not firebase_admin._apps:

    firebase_config = dict(st.secrets["firebase"])

    cred = credentials.Certificate(
        firebase_config
    )

    firebase_admin.initialize_app(
        cred,
        {
            "projectId":
            firebase_config["project_id"]
        }
    )

# ==========================================
# FIRESTORE
# ==========================================

db = firestore.client()

# ==========================================
# FIREBASE AUTH
# ==========================================

auth = firebase_auth

# ==========================================
# GOOGLE OAUTH
# ==========================================

GOOGLE_CLIENT_ID = st.secrets[
    "GOOGLE_CLIENT_ID"
]

GOOGLE_CLIENT_SECRET = st.secrets[
    "GOOGLE_CLIENT_SECRET"
]

GOOGLE_REDIRECT_URI = (
    "https://rag-system-2026.streamlit.app/component/streamlit_oauth.authorize_button"
)
oauth2 = OAuth2Component(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    "https://accounts.google.com/o/oauth2/v2/auth",
    "https://oauth2.googleapis.com/token",
)
