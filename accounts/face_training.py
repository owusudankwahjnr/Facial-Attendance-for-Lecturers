import os
import random
import joblib
import numpy as np
from sklearn.svm import SVC
from deepface import DeepFace
from django.conf import settings

def train_and_save_model(user, model_name="Facenet"):
    user_id = user.id
    user_dir = os.path.join(settings.MEDIA_ROOT, f"user_faces/{user_id}/")
    model_dir = os.path.join(settings.BASE_DIR, f"models/user_models/{user_id}/")
    os.makedirs(model_dir, exist_ok=True)

    user_images = [
        os.path.join(user_dir, f) for f in os.listdir(user_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    if len(user_images) < 10:
        raise ValueError(f"User {user_id} has fewer than 10 images.")

    X, y = [], []

    for img_path in user_images:
        try:
            emb = DeepFace.represent(img_path=img_path, model_name=model_name, enforce_detection=True)[0]["embedding"]
            X.append(emb)
            y.append(1)
        except Exception:
            continue

    other_users_dir = os.path.join(settings.MEDIA_ROOT, "user_faces")
    for other_id in os.listdir(other_users_dir):
        if str(other_id) == str(user_id):
            continue
        other_user_dir = os.path.join(other_users_dir, other_id)
        if not os.path.isdir(other_user_dir):
            continue
        other_images = [
            os.path.join(other_user_dir, f)
            for f in os.listdir(other_user_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        number_of_error = 0
        for img_path in random.sample(other_images, min(25, len(other_images))):

            try:
                emb = DeepFace.represent(img_path=img_path, model_name=model_name, enforce_detection=True)[0]["embedding"]
                X.append(emb)
                y.append(0)
            except Exception:

                continue

    if len(set(y)) < 2:
        raise ValueError("Need both positive and negative samples to train.")

    clf = SVC(probability=True)
    clf.fit(X, y)

    model_path = os.path.join(model_dir, "classifier.joblib")
    joblib.dump(clf, model_path)

    user.model_trained = True
    user.save()
