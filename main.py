import streamlit as st
import pandas as pd

# Linki do oficjalnych danych gov.pl (stan na 22.01.2025)
URL_MESKIE = "https://dane.gov.pl/en/dataset/1681/resource/63892/download"
URL_ZENSKIE = "https://dane.gov.pl/en/dataset/1681/resource/63891/download"

st.set_page_config(page_title="Licznik Nazwisk 2025", page_icon="📊")

st.title("📊 Kalkulator Popularności Nazwisk (PESEL 2025)")
st.markdown("Aplikacja pobiera dane bezpośrednio z serwisu **dane.gov.pl** (stan na styczeń 2025).")

@st.cache_data
def load_data():
    # Pobieranie danych (uproszczone dla demo)
    df_m = pd.read_csv(URL_MESKIE).rename(columns={'Nazwisko aktualne': 'Nazwisko', 'Liczba': 'Mężczyźni'})
    df_f = pd.read_csv(URL_ZENSKIE).rename(columns={'Nazwisko aktualne': 'Nazwisko', 'Liczba': 'Kobiety'})
    return df_m, df_f

try:
    with st.spinner('Pobieranie najnowszej bazy PESEL...'):
        df_m, df_f = load_data()

    nazwisko_input = st.text_input("Wpisz nazwisko:", "NOWAK").upper().strip()

    if nazwisko_input:
        m_count = df_m[df_m['Nazwisko'] == nazwisko_input]['Mężczyźni'].values
        f_count = df_f[df_f['Nazwisko'] == nazwisko_input]['Kobiety'].values
        
        m_val = m_count[0] if len(m_count) > 0 else 0
        f_val = f_count[0] if len(f_count) > 0 else 0
        total = m_val + f_val

        col1, col2, col3 = st.columns(3)
        col1.metric("Suma", f"{total:,}")
        col2.metric("Mężczyźni", f"{m_val:,}")
        col3.metric("Kobiety", f"{f_val:,}")

        if total == 0:
            st.warning("Nie znaleziono nazwiska w bazie lub występuje mniej niż 2 razy.")
        else:
            st.info(f"Nazwisko **{nazwisko_input}** jest wczytane z bazy z 22.01.2025 r.")

except Exception as e:
    st.error(f"Błąd połączenia z bazą gov.pl: {e}")
