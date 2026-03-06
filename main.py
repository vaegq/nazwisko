import streamlit as st
import pandas as pd

# Bezpośrednie linki do zasobów 2025
URL_MESKIE = "https://dane.gov.pl/en/dataset/1681/resource/63892/download"
URL_ZENSKIE = "https://dane.gov.pl/en/dataset/1681/resource/63891/download"

st.set_page_config(page_title="PESEL 2025", layout="centered")

@st.cache_data
def load_data(url):
    try:
        # Próba wczytania z automatycznym separatorem i ignorowaniem błędnych linii
        df = pd.read_csv(url, sep=None, engine='python', encoding='utf-8-sig', on_bad_lines='skip')
        
        # Czyścimy nazwy kolumn ze spacji i niewidocznych znaków
        df.columns = [str(c).strip() for c in df.columns]
        
        # Mapowanie kolumn (szukamy tych, które zawierają kluczowe słowa)
        col_n = next((c for c in df.columns if 'nazwisko' in c.lower()), None)
        col_l = next((c for c in df.columns if 'liczba' in c.lower()), None)
        
        if col_n and col_l:
            return df[[col_n, col_l]].rename(columns={col_n: 'Nazwisko', col_l: 'Liczba'})
        return df
    except Exception as e:
        st.error(f"Problem z plikiem: {e}")
        return pd.DataFrame()

st.title("📊 Licznik Nazwisk - PESEL 2025")

with st.spinner('Łączenie z bazą Ministerstwa...'):
    df_m = load_data(URL_MESKIE)
    df_f = load_data(URL_ZENSKIE)

nazwisko = st.text_input("Wpisz nazwisko:", "NOWAK").strip().upper()

if nazwisko:
    # Bezpieczne wyciąganie wartości
    def get_count(df, n):
        if df.empty or 'Nazwisko' not in df.columns: return 0
        match = df[df['Nazwisko'].astype(str).str.upper() == n]
        return int(match['Liczba'].values[0]) if not match.empty else 0

    m_val = get_count(df_m, nazwisko)
    f_val = get_count(df_f, nazwisko)
    total = m_val + f_val

    st.divider()
    if total > 0:
        c1, c2, c3 = st.columns(3)
        c1.metric("RAZEM", f"{total:,}")
        c2.metric("Mężczyźni", f"{m_val:,}")
        c3.metric("Kobiety", f"{f_val:,}")
        st.success(f"Dane aktualne na styczeń 2025 r.")
    else:
        st.warning(f"Brak nazwiska '{nazwisko}' w bazie (lub występuje < 2 razy).")
    st.divider()

st.caption("Dane pochodzą z portalu dane.gov.pl (Rejestr PESEL).")
