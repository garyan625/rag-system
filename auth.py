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

    cred = credentials.Certificate(
        dict(st.secrets["firebase"])
    )

    firebase_admin.initialize_app(
        cred,
        {
            "projectId":
            st.secrets["FIREBASE_PROJECT_ID"]
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
    "http://localhost:8501/component/streamlit_oauth.authorize_button"
)

oauth2 = OAuth2Component(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    "https://accounts.google.com/o/oauth2/v2/auth",
    "https://oauth2.googleapis.com/token",
)
