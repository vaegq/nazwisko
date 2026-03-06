import streamlit as st
import pandas as pd
import requests
import io

# Linki do zasobów 2025
URL_M = "https://dane.gov.pl/en/dataset/1681/resource/63892/download"
URL_Z = "https://dane.gov.pl/en/dataset/1681/resource/63891/download"

st.set_page_config(page_title="PESEL 2025", layout="centered")

@st.cache_data
def get_pesel_data(url):
    try:
        response = requests.get(url, timeout=10)
        # Próba dekodowania z obsługą różnych formatów polskich znaków
        content = response.content.decode('utf-8-sig', errors='ignore')
        
        # Wczytujemy z automatycznym wykrywaniem separatora
        df = pd.read_csv(io.StringIO(content), sep=None, engine='python', on_bad_lines='skip')
        
        # Usuwamy białe znaki z nagłówków i danych
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Znajdź kolumnę z nazwiskiem i liczbą po słowach kluczowych
        col_n = [c for c in df.columns if 'NAZWISKO' in c][0]
        col_l = [c for c in df.columns if 'LICZBA' in c][0]
        
        df = df[[col_n, col_l]].copy()
        df.columns = ['NAZWISKO', 'LICZBA']
        df['NAZWISKO'] = df['NAZWISKO'].astype(str).str.strip().str.upper()
        df['LICZBA'] = pd.to_numeric(df['LICZBA'], errors='coerce').fillna(0).astype(int)
        
        return df
    except Exception as e:
        return pd.DataFrame()

st.title("📊 Oficjalny Licznik Nazwisk 2025")

with st.spinner('Pobieranie bazy danych...'):
    df_m = get_pesel_data(URL_M)
    df_f = get_pesel_data(URL_Z)

nazwisko = st.text_input("Wpisz nazwisko:", "NOWAK").strip().upper()

if not df_m.empty and not df_f.empty:
    m_val = df_m[df_m['NAZWISKO'] == nazwisko]['LICZBA'].sum()
    f_val = df_f[df_f['NAZWISKO'] == nazwisko]['LICZBA'].sum()
    total = m_val + f_val

    if total > 0:
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("RAZEM", f"{total:,}")
        c2.metric("Mężczyźni", f"{m_val:,}")
        c3.metric("Kobiety", f"{f_val:,}")
        st.divider()
        st.success("Dane załadowane poprawnie.")
    else:
        st.error(f"Nie znaleziono nazwiska {nazwisko}. Sprawdź pisownię.")
else:
    st.error("Błąd pobierania bazy. Sprawdź połączenie z internetem.")
