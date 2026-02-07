import streamlit as st
import pandas as pd
import json

# =====================================================
# KONFIGURACJA STRONY
# =====================================================
st.set_page_config(
    page_title="Znajdź znajomych na kursie",
    page_icon="🤝",
    layout="wide"
)

# =====================================================
# WCZYTANIE DANYCH
# =====================================================
@st.cache_data
def load_data():
    return pd.read_csv("clustered_data_v1.csv")

@st.cache_data
def load_cluster_descriptions():
    with open("cluster_descriptions.json", "r", encoding="utf-8") as f:
        return json.load(f)

df = load_data()
cluster_descriptions = load_cluster_descriptions()

# =====================================================
# NAZWY KLASTRÓW
# =====================================================
CLUSTER_NAMES = {
    0: "🎯 Niezależni Indywidualiści",
    1: "🚀 Aktywni Millennialsi",
    2: "🧠 Doświadczeni Stratedzy",
    3: "🌱 Niekonwencjonalni Odkrywcy"
}

# =====================================================
# FUNKCJA REGUŁOWA – PRZYPISANIE KLASTRA
# =====================================================
def assign_cluster(profile: dict) -> int:
    if profile["generation"] == "Millennialsi" and profile["edu_level"] == "Wyższe":
        return 1
    if profile["generation"] in ["Gen X", "Boomersi"]:
        return 2
    if profile["fav_animals"] == "Inne":
        return 3
    return 0

# =====================================================
# HEADER
# =====================================================
st.title("🤝 Znajdź znajomych na kursie")
st.markdown(
    "<span style='font-size:18px;'>Eksploruj społeczność kursu i znajdź osoby o podobnym profilu</span>",
    unsafe_allow_html=True
)

# =====================================================
# SIDEBAR – FILTRY
# =====================================================
st.sidebar.header("🔎 Filtruj kursantów")

gender_filter = st.sidebar.multiselect(
    "Płeć",
    options=sorted(df["gender"].dropna().unique()),
    default=sorted(df["gender"].dropna().unique())
)

generation_filter = st.sidebar.multiselect(
    "Pokolenie",
    options=sorted(df["generation"].dropna().unique()),
    default=sorted(df["generation"].dropna().unique())
)

filtered_df = df[
    (df["gender"].isin(gender_filter)) &
    (df["generation"].isin(generation_filter))
]

# =====================================================
# EKSPLORACJA SPOŁECZNOŚCI
# =====================================================
st.subheader("📊 Eksploracja społeczności kursu")
st.markdown(f"**Liczba kursantów po filtrach:** {len(filtered_df)}")

cluster_counts = (
    filtered_df["Cluster"]
    .value_counts()
    .sort_index()
    .reset_index()
)

cluster_counts.columns = ["Cluster", "Liczba"]
cluster_counts["Profil klastra"] = cluster_counts["Cluster"].map(CLUSTER_NAMES)

st.bar_chart(
    cluster_counts.set_index("Profil klastra")["Liczba"],
    height=300
)

# =====================================================
# ZNAJDŹ SWÓJ PROFIL
# =====================================================
st.divider()
st.subheader("🧬 Znajdź swój profil")

with st.form("profile_form"):
    generation = st.selectbox(
        "Pokolenie",
        sorted(df["generation"].dropna().unique())
    )
    edu_level = st.selectbox(
        "Wykształcenie",
        sorted(df["edu_level"].dropna().unique())
    )
    fav_animals = st.selectbox(
        "Ulubione zwierzęta",
        sorted(df["fav_animals"].dropna().unique())
    )
    fav_place = st.selectbox(
        "Ulubione miejsce",
        sorted(df["fav_place"].dropna().unique())
    )
    gender = st.selectbox(
        "Płeć",
        sorted(df["gender"].dropna().unique())
    )

    submitted = st.form_submit_button("🔍 Znajdź mój profil")

if submitted:
    user_profile = {
        "generation": generation,
        "edu_level": edu_level,
        "fav_animals": fav_animals,
        "fav_place": fav_place,
        "gender": gender
    }

    cluster_id = assign_cluster(user_profile)
    cluster_name = CLUSTER_NAMES[cluster_id]
    cluster_desc = cluster_descriptions[str(cluster_id)]

    st.success(f"✨ Twój profil społeczny: **{cluster_name}**")
    st.markdown(cluster_desc)

    similar_people = filtered_df[filtered_df["Cluster"] == cluster_id]

    st.markdown("### 👥 Osoby o podobnym profilu")
    st.dataframe(
        similar_people[
            [
                "generation",
                "gender",
                "edu_level",
                "fav_animals",
                "fav_place"
            ]
        ].head(10),
        width="stretch"
    )

# =====================================================
# STOPKA
# =====================================================
st.divider()
st.caption("Projekt: Znajdź znajomych na kursie przygotował Dariusz Klimkiewicz")


