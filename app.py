import requests
import streamlit as st

BASE_URL = "https://api.alquran.cloud/v1"

st.set_page_config(page_title="Quran Explorer", page_icon="📖", layout="wide")


@st.cache_data(show_spinner=False)
def get_surah_list() -> list[dict]:
    response = requests.get(f"{BASE_URL}/surah", timeout=20)
    response.raise_for_status()
    return response.json()["data"]


@st.cache_data(show_spinner=False)
def get_surah_ayahs(surah_number: int, edition: str) -> list[dict]:
    response = requests.get(f"{BASE_URL}/surah/{surah_number}/{edition}", timeout=20)
    response.raise_for_status()
    return response.json()["data"]["ayahs"]


st.title("📖 Quran Explorer")
st.caption("Read Quranic verses with translations and quick navigation by Surah.")

with st.sidebar:
    st.header("Settings")
    edition_options = {
        "Arabic (Uthmani)": "quran-uthmani",
        "English (Sahih International)": "en.sahih",
        "Urdu (Jalandhry)": "ur.jalandhry",
    }

    selected_edition_label = st.selectbox("Text edition", list(edition_options.keys()))
    selected_edition = edition_options[selected_edition_label]

try:
    surahs = get_surah_list()
except requests.RequestException:
    st.error(
        "Could not load Quran data right now. Please check your internet connection and try again."
    )
    st.stop()

surah_map = {
    f"{surah['number']}. {surah['englishName']} ({surah['name']})": surah["number"]
    for surah in surahs
}

selected_surah_label = st.selectbox("Choose Surah", list(surah_map.keys()))
selected_surah_number = surah_map[selected_surah_label]

try:
    ayahs = get_surah_ayahs(selected_surah_number, selected_edition)
except requests.RequestException:
    st.error("Could not load verses for the selected Surah. Please try again.")
    st.stop()

st.subheader(selected_surah_label)

verse_count = len(ayahs)
start_ayah, end_ayah = st.slider(
    "Verse range",
    min_value=1,
    max_value=verse_count,
    value=(1, min(10, verse_count)),
)

for ayah in ayahs[start_ayah - 1 : end_ayah]:
    st.markdown(f"**{ayah['numberInSurah']}.** {ayah['text']}")

st.info("Data source: api.alquran.cloud")
