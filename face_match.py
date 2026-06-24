import sqlite3
import json
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )

def find_user(current_embedding):

    conn = sqlite3.connect("mindmate.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id,name,email,embedding FROM users"
    )

    users = cursor.fetchall()

    conn.close()

    best_score = 0
    best_user = None

    for user in users:

        saved_embedding = np.array(
            json.loads(user[3])
        )

        score = cosine_similarity(
            current_embedding,
            saved_embedding
        )

        print(f"{user[1]} -> {score:.4f}")

        if score > best_score:
            best_score = score
            best_user = user

    if best_score > 0.60:
        return best_user

    return None