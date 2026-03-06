import streamlit as st
import pandas as pd

# Linki do danych (stan na styczeń 2025)
URL_MESKIE = "https://dane.gov.pl/en/dataset/1681/resource/63892/download"
URL_ZENSKIE = "https://dane.gov.pl/en/dataset/1681/resource/63891/download"

st.set_page_config(page_title="Licznik Nazwisk 2025", page_icon="📊", layout="wide")

@st.cache_data
def load_data(url):
    # Próbujemy wczytać dane z różnymi zabezpieczeniami
    try:
        # engine='python' jest wolniejszy, ale lepiej radzi sobie z błędami tokenizacji
        df = pd.read_csv(
            url, 
            sep=';', 
            encoding='utf-8', 
            on_bad_lines='skip', 
            engine='python'
        )
        # Standaryzacja nazw kolumn (usuwamy spacje i zmieniamy wielkość liter)
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Błąd przy wczytywaniu {url}: {e}")
        return pd.DataFrame()

st.title("📊 Kalkulator Nazwisk 2025")
st.info("Aplikacja pobiera dane bezpośrednio z rejestru PESEL (stan na 2025).")

try:
    with st.spinner('Pobieranie i czyszczenie bazy danych...'):
        df_m = load_data(URL_MESKIE)
        df_f = load_data(URL_ZENSKIE)

    nazwisko_input = st.text_input("Wpisz nazwisko:", "NOWAK").upper().strip()

    if nazwisko_input:
        # Szukamy w kolumnach 'Nazwisko aktualne' i 'Liczba'
        # Uwaga: w plikach gov.pl nazwy kolumn mogą się różnić, np. 'NAZWISKO_AKTUALNE'
        # Sprawdzamy możliwe warianty nazw kolumn
        col_nazwisko = 'Nazwisko aktualne' if 'Nazwisko aktualne' in df_m.columns else df_m.columns[0]
        col_liczba = 'Liczba' if 'Liczba' in df_m.columns else df_m.columns[1]

        m_res = df_m[df_m[col_nazwisko].astype(str).str.upper() == nazwisko_input]
        f_res = df_f[df_f[col_nazwisko].astype(str).str.upper() == nazwisko_input]
        
        m_val = int(m_res[col_liczba].values[0]) if not m_res.empty else 0
        f_val = int(f_res[col_liczba].values[0]) if not f_res.empty else 0
        total = m_val + f_val

        st.markdown(f"### Wyniki dla nazwiska: **{nazwisko_input}**")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Suma", f"{total:,}")
        c2.metric("Mężczyźni ♂", f"{m_val:,}")
        c3.metric("Kobiety ♀", f"{f_val:,}")

        if total == 0:
            st.warning("Nie znaleziono nazwiska lub występuje mniej niż 2 razy (limit RODO).")

except Exception as e:
    st.error(f"Błąd krytyczny: {e}")
