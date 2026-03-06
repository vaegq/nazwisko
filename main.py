import streamlit as st
import pandas as pd

# Linki do danych (stan na styczeń 2025)
URL_MESKIE = "https://dane.gov.pl/en/dataset/1681/resource/63892/download"
URL_ZENSKIE = "https://dane.gov.pl/en/dataset/1681/resource/63891/download"

st.set_page_config(page_title="Licznik Nazwisk 2025", page_icon="📊")

@st.cache_data
def load_data():
    # Dodano sep=';' oraz encoding='utf-8' dla poprawnego odczytu bazy gov.pl
    df_m = pd.read_csv(URL_MESKIE, sep=';', encoding='utf-8').rename(
        columns={'Nazwisko aktualne': 'Nazwisko', 'Liczba': 'Mężczyźni'}
    )
    df_f = pd.read_csv(URL_ZENSKIE, sep=';', encoding='utf-8').rename(
        columns={'Nazwisko aktualne': 'Nazwisko', 'Liczba': 'Kobiety'}
    )
    return df_m, df_f

st.title("📊 Kalkulator Nazwisk 2025")

try:
    with st.spinner('Pobieranie bazy danych z serwerów rządowych...'):
        df_m, df_f = load_data()

    nazwisko_input = st.text_input("Wpisz nazwisko (bez polskich znaków lub z nimi):", "NOWAK").upper().strip()

    if nazwisko_input:
        # Filtracja
        m_res = df_m[df_m['Nazwisko'] == nazwisko_input]
        f_res = df_f[df_f['Nazwisko'] == nazwisko_input]
        
        m_val = int(m_res['Mężczyźni'].values[0]) if not m_res.empty else 0
        f_val = int(f_res['Kobiety'].values[0]) if not f_res.empty else 0
        total = m_val + f_val

        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("Łącznie", f"{total:,}")
        col2.metric("Mężczyźni", f"{m_val:,}")
        col3.metric("Kobiety", f"{f_val:,}")
        st.divider()

        if total == 0:
            st.warning("Nie znaleziono nazwiska. Upewnij się, że wpisano je poprawnie.")
        else:
            st.success(f"Dane na rok 2025 dla nazwiska: {nazwisko_input}")

except Exception as e:
    st.error(f"Wystąpił problem: {e}")
    st.info("Spróbuj pobrać plik ręcznie z dane.gov.pl, aby sprawdzić czy format się nie zmienił.")
