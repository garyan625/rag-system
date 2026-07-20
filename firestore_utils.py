from firestore import db
from datetime import datetime


def save_message(
    email,
    role,
    content
):

    db.collection("chat_history")\
      .document(email)\
      .collection("messages")\
      .add(
        {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        }
    )


def load_messages(email):

    docs = (
        db.collection("chat_history")
        .document(email)
        .collection("messages")
        .order_by("timestamp")
        .stream()
    )

    messages = []

    for doc in docs:

        data = doc.to_dict()

        messages.append(
            {
                "role": data["role"],
                "content": data["content"]
            }
        )

    return messages
