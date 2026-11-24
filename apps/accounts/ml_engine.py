"""
ML Prediction Engine
Trains ensemble models on the student dataset and predicts performance profile.
"""
import os
import time
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier, VotingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from django.conf import settings


def get_dataset_path():
    """Resolve path to Datasets.csv — tries workspace root and settings path."""
    configured = getattr(settings, 'DATASETS_CSV', None)
    if configured and os.path.exists(str(configured)):
        return str(configured)
    fallback = os.path.join(os.path.dirname(settings.BASE_DIR), 'Datasets.csv')
    if os.path.exists(fallback):
        return fallback
    # Try same directory as manage.py
    base = str(settings.BASE_DIR)
    p = os.path.join(base, 'Datasets.csv')
    if os.path.exists(p):
        return p
    return None


def train_all_models():
    """
    Trains all ML models on the student dataset.
    Returns a list of dicts with model accuracy metrics.
    Saves results to AlgorithmAccuracy model.
    """
    from apps.accounts.models import AlgorithmAccuracy

    dataset_path = get_dataset_path()
    if not dataset_path:
        return None, "Dataset file (Datasets.csv) not found. Please place it in the project root."

    df = pd.read_csv(dataset_path, encoding='latin-1')

    if 'Label' not in df.columns or 'Fid' not in df.columns:
        return None, "Dataset missing required columns: 'Label', 'Fid'."

    df['Label'] = df['Label'].apply(lambda x: 0 if x == 0 else 1)

    cv = CountVectorizer()
    X = cv.fit_transform(df['Fid'].apply(str))
    y = df['Label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    AlgorithmAccuracy.objects.all().delete()

    results = []
    model_list = []

    algo_configs = [
        ('Artificial Neural Network (ANN)', MLPClassifier(max_iter=500, random_state=42)),
        ('Naive Bayes', MultinomialNB()),
        ('Support Vector Machine (SVM)', svm.LinearSVC(max_iter=2000, random_state=42)),
        ('Logistic Regression', LogisticRegression(solver='lbfgs', max_iter=500, random_state=42)),
        ('Gradient Boosting', GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=42)),
        ('Decision Tree', DecisionTreeClassifier(random_state=42)),
        ('K-Nearest Neighbors (KNN)', KNeighborsClassifier()),
    ]

    for name, model in algo_configs:
        try:
            start = time.time()
            model.fit(X_train, y_train)
            elapsed = round(time.time() - start, 3)

            y_pred = model.predict(X_test)
            acc = round(accuracy_score(y_test, y_pred) * 100, 2)
            prec = round(precision_score(y_test, y_pred, zero_division=0) * 100, 2)
            rec = round(recall_score(y_test, y_pred, zero_division=0) * 100, 2)
            f1 = round(f1_score(y_test, y_pred, zero_division=0) * 100, 2)

            # For voting, only add classifiers that support predict_proba or decision_function
            short_key = name.split(' ')[0].lower()
            model_list.append((short_key, model))

            AlgorithmAccuracy.objects.create(
                name=name,
                accuracy=acc,
                precision_score=prec,
                recall_score=rec,
                f1_score=f1,
                execution_time=elapsed,
            )
            results.append({
                'name': name,
                'accuracy': acc,
                'precision': prec,
                'recall': rec,
                'f1': f1,
                'time': elapsed,
            })
        except Exception as e:
            results.append({'name': name, 'error': str(e)})

    return results, None


def predict_student(fid, math_score=0, reading_score=0, writing_score=0,
                    age=None, gender=None, parental_edu=None,
                    test_prep=None, lunch=None, **kwargs):
    """
    Predict a single student's profile using an ensemble voting classifier.
    Returns prediction label string.
    """
    dataset_path = get_dataset_path()
    if not dataset_path:
        return 'Poor', {}, "Dataset not found"

    df = pd.read_csv(dataset_path, encoding='latin-1')
    df['Label'] = df['Label'].apply(lambda x: 0 if x == 0 else 1)

    cv = CountVectorizer()
    X = cv.fit_transform(df['Fid'].apply(str))
    y = df['Label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    models_v = [
        ('mlp', MLPClassifier(max_iter=500, random_state=42)),
        ('nb', MultinomialNB()),
        ('svm', svm.LinearSVC(max_iter=2000, random_state=42)),
        ('lr', LogisticRegression(solver='lbfgs', max_iter=500, random_state=42)),
        ('gb', GradientBoostingClassifier(n_estimators=100, random_state=42)),
        ('dt', DecisionTreeClassifier(random_state=42)),
    ]

    voting = VotingClassifier(estimators=models_v, voting='hard')
    voting.fit(X_train, y_train)

    input_vec = cv.transform([str(fid)]).toarray()
    pred_num = int(voting.predict(input_vec)[0])

    # Enrich prediction with score-based logic for more granularity
    avg = (int(math_score or 0) + int(reading_score or 0) + int(writing_score or 0)) / 3
    if pred_num == 0:
        if avg >= 80:
            label = 'Excellent'
        else:
            label = 'Good'
    else:
        if avg >= 50:
            label = 'Average'
        else:
            label = 'Poor'

    return label, {}, None
