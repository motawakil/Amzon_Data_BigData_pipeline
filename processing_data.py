import pandas as pd
import re
import os
from sklearn.model_selection import train_test_split

# === Fonctions utilitaires ===

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s\d]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Liens
    text = re.sub(r'<.*?>', '', text)  # HTML
    text = re.sub(r'\d+', '', text)  # Chiffres
    return text

def to_label(score):
    if score < 3:
        return 0  # négatif
    elif score == 3:
        return 1  # neutre
    else:
        return 2  # positif

# === Chargement des données ===
print("📥 Chargement de Data.json ...")
df = pd.read_json("Data.json", lines=True)
print(f"🔢 Lignes AVANT filtrage : {len(df)}")

# === Suppression des lignes incomplètes ===
df = df.dropna(subset=["reviewText", "overall"])
print(f"🧹 Lignes après suppression des valeurs manquantes : {len(df)}")

# === Split AVANT nettoyage ===
X_train, X_temp, y_train, y_temp = train_test_split(
    df, df["overall"], test_size=0.2, random_state=42, stratify=df["overall"]
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
)

print(f"\n📂 Répartition initiale :")
print(f" - Train : {len(X_train)}")
print(f" - Validation : {len(X_val)}")
print(f" - Test (non nettoyé) : {len(X_test)}")

# === Nettoyage et label uniquement pour train et validation ===

def preprocess(df_part):
    df_part = df_part.copy()
    df_part["reviewText"] = df_part["reviewText"].astype(str).apply(clean_text)
    df_part["summary"] = df_part["summary"].astype(str).apply(clean_text)
    df_part["reviewerName"] = df_part["reviewerName"].astype(str).apply(clean_text)
    df_part["label"] = df_part["overall"].apply(to_label)
    return df_part

X_train_clean = preprocess(X_train)
X_val_clean = preprocess(X_val)
X_test_raw = X_test.copy().drop(columns=["label"], errors='ignore')  # Pas de nettoyage ni label

# === Sauvegarde ===
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

X_train_clean.to_json(os.path.join(output_dir, "train_data.json"), orient="records", lines=True, force_ascii=False)
X_val_clean.to_json(os.path.join(output_dir, "validation_data.json"), orient="records", lines=True, force_ascii=False)
X_test_raw.to_json(os.path.join(output_dir, "test_data_amazon.json"), orient="records", lines=True, force_ascii=False)

# === Statistiques ===
label_counts = X_train_clean["label"].value_counts().sort_index()
print("\n📊 Répartition des classes dans l'entraînement :")
print(f" - Négatif (0) : {label_counts.get(0, 0)}")
print(f" - Neutre  (1) : {label_counts.get(1, 0)}")
print(f" - Positif (2) : {label_counts.get(2, 0)}")

print("\n✅ Données sauvegardées dans /data :")
print(" - train_data.json (nettoyé + label)")
print(" - validation_data.json (nettoyé + label)")
print(" - test_data_amazon.json (non nettoyé, sans label)")
