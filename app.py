# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19Ru5XEbPYFKAacxFVzJUUu0PWASckEgu
"""

from google.colab import files
uploded = files.upload()

from google.colab import files
import pandas as pd # Import pandas to work with DataFrames

uploaded = files.upload()

# Assuming your uploaded file is a CSV, read it into a DataFrame
import io
filename = list(uploaded.keys())[0]  # Get the filename of the uploaded file
df = pd.read_csv(io.BytesIO(uploaded[filename]))  # Read the file into a DataFrame


# Genel bilgiler
df.info()

# Eksik değer kontrolü
print("\nEksik değer var mı?\n", df.isnull().sum())

# Sınıf dağılımı
print("\nSınıf Dağılımı:\n", df['Class'].value_counts(normalize=True))

import seaborn as sns
import matplotlib.pyplot as plt

sns.boxplot(x=df['Amount'])
plt.title('Amount sütunundaki aykırı değerler')
plt.show()

from sklearn.preprocessing import StandardScaler

# Yeni sütunlar oluşturalım
scaler = StandardScaler()
df['norm_Amount'] = scaler.fit_transform(df[['Amount']])
df['norm_Time'] = scaler.fit_transform(df[['Time']])

# Orijinal 'Amount' ve 'Time' sütunlarını düşürelim
df = df.drop(['Amount', 'Time'], axis=1)

df.head()

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Korelasyon matrisi
corr_matrix = df.corr()

# Hedef sınıfla olan korelasyona bakalım
cor_target = abs(corr_matrix['Class'])
selected_features_corr = cor_target[cor_target > 0.1].index.tolist()

print("Korelasyon yöntemi ile seçilen özellikler:")
print(selected_features_corr)

from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import MinMaxScaler

X = df.drop('Class', axis=1)
y = df['Class']

# Chi2 için veriler negatif olmamalı, bu yüzden MinMaxScaler
X_minmax = MinMaxScaler().fit_transform(X)

selector = SelectKBest(score_func=chi2, k=10)
selector.fit(X_minmax, y)

selected_features_kbest = X.columns[selector.get_support()].tolist()

print("SelectKBest yöntemi ile seçilen özellikler:")
print(selected_features_kbest)

from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier()
model.fit(X, y)

feature_importances = pd.Series(model.feature_importances_, index=X.columns)
selected_features_rf = feature_importances.sort_values(ascending=False).head(10).index.tolist()

print("Random Forest ile seçilen önemli özellikler:")
print(selected_features_rf)

from sklearn.model_selection import train_test_split

# 3 farklı özellik kümesi
X1 = df[selected_features_corr]
X2 = df[selected_features_kbest]
X3 = df[selected_features_rf]
y = df['Class']

# Eğitim-test bölünmesi (hepsi için aynı y kullanılacak)
X1_train, X1_test, y_train, y_test = train_test_split(X1, y, test_size=0.3, random_state=42, stratify=y)
X2_train, X2_test, _, _ = train_test_split(X2, y, test_size=0.3, random_state=42, stratify=y)
X3_train, X3_test, _, _ = train_test_split(X3, y, test_size=0.3, random_state=42, stratify=y)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(),
    "KNN": KNeighborsClassifier(),
    "SVM": SVC()
}

from sklearn.metrics import ConfusionMatrixDisplay

feature_sets = {
    "Korelasyon Seçimi": (X1_train, X1_test),
    "SelectKBest Seçimi": (X2_train, X2_test),
    "Random Forest Seçimi": (X3_train, X3_test)
}

for fs_name, (X_train, X_test) in feature_sets.items():
    print(f"\n🔹 Özellik Seti: {fs_name}")
    for model_name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print(f"\nModel: {model_name}")
        cm = confusion_matrix(y_test, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot()
        plt.title(f'{model_name} - {fs_name}')
        plt.show()

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:,1] if hasattr(model, "predict_proba") else model.decision_function(X_test)

    return {
        'Accuracy': accuracy_score(y_test, y_pred),
        'Precision': precision_score(y_test, y_pred),
        'Recall': recall_score(y_test, y_pred),
        'F1 Score': f1_score(y_test, y_pred),
        'ROC AUC': roc_auc_score(y_test, y_prob)
    }


def display_dataframe_to_user(name, dataframe):
  """Displays a Pandas DataFrame to the user.
  Args:
    name: The name of the DataFrame.
    dataframe: The Pandas DataFrame to display.
  """
  print(f"{name}:\n")
  print(dataframe)

results = []

for fs_name, (X_train, X_test) in feature_sets.items():
    for model_name, model in models.items():
        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test)
        metrics.update({
            'Model': model_name,
            'Feature Set': fs_name
        })
        results.append(metrics)

# Sonuçları DataFrame olarak göster
results_df = pd.DataFrame(results)

# Define the display_dataframe_to_user function (ace_tools module replacement)
def display_dataframe_to_user(name, dataframe):
  """Displays a Pandas DataFrame to the user.
  Args:
    name: The name of the DataFrame.
    dataframe: The Pandas DataFrame to display.
  """
  print(f"{name}:\n")
  print(dataframe)

# Call the function to display the results
display_dataframe_to_user(name="Model Karşılaştırma Sonuçları", dataframe=results_df)

import joblib

# Örneğin Random Forest + RF özellikleri en iyiyse:
best_model = RandomForestClassifier()
best_model.fit(X3_train, y_train)

# Use the original DataFrame or a copy before dropping columns to access 'Amount' and 'Time'
original_df = pd.read_csv(io.BytesIO(uploaded[filename]))  # Assuming you still have the uploaded file

# Scaler (sadece norm_Amount ve norm_Time için)
scaler_amount = StandardScaler()
scaler_amount.fit(original_df[['Amount']])  # Use original_df here
scaler_time = StandardScaler()
scaler_time.fit(original_df[['Time']])  # Use original_df here

# Kaydet
joblib.dump(best_model, 'model.pkl')
joblib.dump((scaler_amount, scaler_time), 'scaler.pkl')
