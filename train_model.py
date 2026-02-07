import pandas as pd
import re
from pycaret.clustering import setup, create_model, assign_model, save_model

# ======================
# Wczytanie danych
# ======================
df = pd.read_csv(
    "welcome_survey_simple_v2.csv",
    sep=";"
)

# ======================
# Przygotowanie wieku → pokolenie
# ======================
def age_range_to_number(age):
    if pd.isna(age):
        return None
    age = str(age)
    match = re.match(r"(\d+)\s*-\s*(\d+)", age)
    if match:
        start, end = match.groups()
        return (int(start) + int(end)) / 2
    try:
        return float(age)
    except:
        return None

df["age_numeric"] = df["age"].apply(age_range_to_number)

def map_generation(age):
    if pd.isna(age):
        return "Nieznane"
    if age <= 25:
        return "Gen Z"
    elif age <= 40:
        return "Millennialsi"
    elif age <= 55:
        return "Gen X"
    else:
        return "Boomersi"

df["generation"] = df["age_numeric"].apply(map_generation)

# ======================
# WYBÓR CECH DO MODELU
# ======================
features = [
    "generation",
    "gender",
    "fav_animals",
    "fav_place",
    "edu_level"
]

model_df = df[features].copy()

# ======================
# PyCaret setup
# ======================
setup(
    data=model_df,
    normalize=True,
    session_id=42,
    verbose=True
)

# ======================
# Model klastrów
# ======================
kmeans = create_model(
    "kmeans",
    num_clusters=4
)

# ======================
# Przypisanie klastrów
# ======================
clustered_df = assign_model(kmeans)

# ======================
# Zapis modelu
# ======================
save_model(
    kmeans,
    "friends_clustering_model_v1"
)

# ======================
# Zapis danych z klastrami (do analizy)
# ======================
clustered_df.to_csv(
    "clustered_data_v1.csv",
    index=False
)

print("✅ Model wytrenowany i zapisany")
print("📁 friends_clustering_model_v1.pkl")
print("📁 clustered_data_v1.csv")
