import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression


def train(features, labels):
    model = LogisticRegression(max_iter=200, class_weight="balanced", random_state=17)
    model.fit(np.asarray(features), np.asarray(labels))
    return model


def probability(model, features):
    return model.predict_proba(np.asarray(features))[:, 1]


def save(model, path):
    joblib.dump(model, path)