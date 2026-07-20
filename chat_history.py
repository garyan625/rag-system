from firebase_db import db
from datetime import datetime


# ==========================================
# SAVE MESSAGE
# ==========================================

def save_message(
    email,
    role,
    message
):

    db.collection("users") \
      .document(email) \
      .collection("chat_history") \
      .add(
          {
              "role": role,
              "message": message,
              "timestamp": datetime.utcnow()
          }
      )


# ==========================================
# LOAD CHAT HISTORY
# ==========================================

def load_chat_history(email):

    messages = []

    docs = (
        db.collection("users")
        .document(email)
        .collection("chat_history")
        .order_by("timestamp")
        .stream()
    )

    for doc in docs:

        data = doc.to_dict()

        messages.append(
            {
                "role": data.get(
                    "role",
                    "assistant"
                ),
                "content": data.get(
                    "message",
                    ""
                )
            }
        )

    return messages


# ==========================================
# CLEAR CHAT HISTORY
# ==========================================

def clear_chat_history(email):

    docs = (
        db.collection("users")
        .document(email)
        .collection("chat_history")
        .stream()
    )

    for doc in docs:
        doc.reference.delete()
