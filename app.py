import streamlit as st
import pandas as pd
import json
import re
import altair as alt

# ======================
# Konfiguracja strony
# ======================
st.set_page_config(
    page_title="Znajdź znajomych na kursie",
    layout="wide"
)

# ======================
# Wczytanie danych
# ======================
@st.cache_data
def load_clustered_data():
    return pd.read_csv("clustered_data_v1.csv")

with open("cluster_descriptions.json", "r", encoding="utf-8") as f:
    CLUSTER_DESCRIPTIONS = json.load(f)

df = load_clustered_data()


# ======================
# SIDEBAR – FILTRY
# ======================
st.sidebar.header("🔍 Filtruj kursantów")

generation_filter = st.sidebar.multiselect(
    "Pokolenie",
    sorted(df["generation"].dropna().unique())
)

gender_filter = st.sidebar.multiselect(
    "Płeć",
    sorted(df["gender"].dropna().unique())
)

animals_filter = st.sidebar.multiselect(
    "Ulubione zwierzęta",
    sorted(df["fav_animals"].dropna().unique())
)

place_filter = st.sidebar.multiselect(
    "Ulubione miejsca",
    sorted(df["fav_place"].dropna().unique())
)

edu_filter = st.sidebar.multiselect(
    "Wykształcenie",
    sorted(df["edu_level"].dropna().unique())
)

# ======================
# FILTROWANIE DANYCH
# ======================
filtered_df = df.copy()

if generation_filter:
    filtered_df = filtered_df[filtered_df["generation"].isin(generation_filter)]
if gender_filter:
    filtered_df = filtered_df[filtered_df["gender"].isin(gender_filter)]
if animals_filter:
    filtered_df = filtered_df[filtered_df["fav_animals"].isin(animals_filter)]
if place_filter:
    filtered_df = filtered_df[filtered_df["fav_place"].isin(place_filter)]
if edu_filter:
    filtered_df = filtered_df[filtered_df["edu_level"].isin(edu_filter)]

# ======================
# TYTUŁ + OPIS
# ======================
st.title("🤝 Znajdź znajomych na kursie")

st.markdown(
    f"""
    <div style="font-size:20px; margin-bottom: 24px;">
        Eksploruj społeczność kursu i znajdź osoby o podobnym profilu
        <span style="color:#666;">({len(filtered_df)} kursantów po filtrach)</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ======================
# WYKRES: Profile kursantów – podział na płeć
# ======================
st.subheader("📊 Profile kursantów – podział na płeć")

plot_df = (
    filtered_df
    .groupby(["Cluster", "gender"])
    .size()
    .reset_index(name="Liczba")
)

plot_df["Profil"] = plot_df["Cluster"].map(
    lambda x: CLUSTER_DESCRIPTIONS.get(x, {}).get("name", x)
)

chart = alt.Chart(plot_df).mark_bar().encode(
    y=alt.Y(
        "Profil:N",
        sort="-x",
        title=None,
        axis=alt.Axis(labelFontSize=14, labelLimit=0, labelPadding=12)
    ),
    x=alt.X(
        "Liczba:Q",
        title=None,
        axis=alt.Axis(labels=False, ticks=False, domain=False)
    ),
    color=alt.Color(
        "gender:N",
        title="Płeć",
        scale=alt.Scale(scheme="set2")
    ),
    tooltip=["Profil", "gender", "Liczba"]
).properties(
    height=420
).configure_view(
    strokeWidth=0
).configure_axis(
    grid=False
)

st.altair_chart(chart, width="stretch")

# ======================
# SEKCJA: ZNAJDŹ SWÓJ PROFIL
# ======================
st.markdown("---")
st.header("🧑‍🤝‍🧑 Znajdź swój profil")

def age_range_to_number(age):
    age = str(age)

    match = re.match(r"(\d+)\s*-\s*(\d+)", age)
    if match:
        a, b = match.groups()
        return (int(a) + int(b)) / 2

    if age.endswith("+"):
        return int(age.replace("+", ""))

    return None


def map_generation(age):
    if age is None:
        return "Nieznane"
    if age <= 25:
        return "Gen Z"
    elif age <= 40:
        return "Millennialsi"
    elif age <= 55:
        return "Gen X"
    else:
        return "Boomersi"


with st.form("user_form"):
    age = st.selectbox(
        "Przedział wiekowy",
        ["18-24", "25-34", "35-44", "45-54", "55+"]
    )
    edu_level = st.selectbox(
        "Wykształcenie",
        ["Podstawowe", "Średnie", "Wyższe"]
    )
    fav_animals = st.selectbox(
        "Ulubione zwierzęta",
        ["Psy", "Koty", "Koty i Psy", "Inne", "Brak ulubionych"]
    )
    fav_place = st.selectbox(
        "Ulubione miejsce",
        ["W górach", "Nad wodą", "W lesie", "Inne"]
    )
    gender = st.selectbox(
        "Płeć",
        ["Kobieta", "Mężczyzna"]
    )

    submit = st.form_submit_button("🔍 Znajdź mój profil")

if submit:
    age_num = age_range_to_number(age)
    generation = map_generation(age_num)

    user_profile = {
        "generation": generation,
        "gender": gender,
        "fav_animals": fav_animals,
        "fav_place": fav_place,
        "edu_level": edu_level,
    }

    # --- Punktowe dopasowanie profilu (cloud-safe) ---
    def similarity_score(row, profile):
        score = 0
        for key, value in profile.items():
            if row[key] == value:
                score += 1
        return score

    scored_df = df.copy()
    scored_df["score"] = scored_df.apply(
        lambda row: similarity_score(row, user_profile),
        axis=1
    )

    # wybieramy klaster z najwyższą średnią punktów
    cluster_id = (
        scored_df
        .groupby("Cluster")["score"]
        .mean()
        .idxmax()
    )

    info = CLUSTER_DESCRIPTIONS.get(cluster_id, {})

    st.markdown("---")
    st.subheader("✨ Twój profil społeczny")
    st.markdown(f"### {info.get('name', cluster_id)}")
    st.write(info.get("description", "Brak opisu profilu."))

    st.info(
        "Profil został dopasowany na podstawie podobieństwa cech "
        "do uczestników kursu."
    )

# ======================
# STOPKA
# ======================
st.caption("Aplikacja: Znajdź znajomych na kursie przygotował Dariusz Klimkiewicz")
