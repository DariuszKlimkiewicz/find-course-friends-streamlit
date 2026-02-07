import pandas as pd

# ======================
# Wczytanie danych z klastrami
# ======================
df = pd.read_csv("clustered_data_v1.csv")

# Nazwa kolumny z klastrem (PyCaret)
CLUSTER_COL = "Cluster"

print("📊 Liczba obserwacji:", len(df))
print("📊 Liczba klastrów:", df[CLUSTER_COL].nunique())
print("\n")

# ======================
# 1️⃣ Wielkość klastrów
# ======================
print("🔹 Wielkość klastrów")
print(df[CLUSTER_COL].value_counts())
print("\n")

# ======================
# 2️⃣ Profil klastrów – cechy kategoryczne
# ======================
categorical_cols = [
    "generation",
    "gender",
    "fav_animals",
    "fav_place",
    "edu_level"
]

for cluster_id in sorted(df[CLUSTER_COL].unique()):
    print("=" * 60)
    print(f"🧩 KLASTER {cluster_id}")
    print("=" * 60)

    cluster_df = df[df[CLUSTER_COL] == cluster_id]

    print(f"Liczba osób: {len(cluster_df)}\n")

    for col in categorical_cols:
        print(f"➡️ {col}")
        print(
            cluster_df[col]
            .value_counts(normalize=True)
            .round(2)
        )
        print()

# ======================
# 3️⃣ Średni wiek (pomocniczo)
# ======================
if "age_numeric" in df.columns:
    print("=" * 60)
    print("📐 Średni wiek w klastrach (pomocniczo)")
    print("=" * 60)
    print(
        df.groupby(CLUSTER_COL)["age_numeric"]
        .mean()
        .round(1)
    )
