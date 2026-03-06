import streamlit as st
import pandas as pd
import requests
import io
import urllib3

# Wyłączenie ostrzeżeń o certyfikatach SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Linki 2025
URL_M = "https://dane.gov.pl/en/dataset/1681/resource/63892/download"
URL_Z = "https://dane.gov.pl/en/dataset/1681/resource/63891/download"

st.set_page_config(page_title="Licznik PESEL 2025", layout="centered")

@st.cache_data(ttl=3600)
def download_data(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        # verify=False pomaga, gdy system ma stare certyfikaty SSL
        r = requests.get(url, headers=headers, verify=False, timeout=30)
        r.raise_for_status()
        
        # Próba odczytu z różnymi separatorami
        data = r.content.decode('utf-8-sig', errors='ignore')
        df = pd.read_csv(io.StringIO(data), sep=None, engine='python', on_bad_lines='skip')
        
        # Standaryzacja kolumn
        df.columns = [str(c).strip().upper() for c in df.columns]
        col_n = next((c for c in df.columns if 'NAZWISKO' in c), None)
        col_l = next((c for c in df.columns if 'LICZBA' in c), None)
        
        if col_n and col_l:
            res = df[[col_n, col_l]].copy()
            res.columns = ['N', 'L']
            res['N'] = res['N'].astype(str).str.strip().str.upper()
            res['L'] = pd.to_numeric(res['L'], errors='coerce').fillna(0).astype(int)
            return res
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Szczegóły techniczne błędu: {e}")
        return pd.DataFrame()

st.title("📊 PESEL 2025 - Wyszukiwarka")

if st.button('🚀 Załaduj / Odśwież bazę danych'):
    st.session_state.df_m = download_data(URL_M)
    st.session_state.df_z = download_data(URL_Z)

if 'df_m' in st.session_state and not st.session_state.df_m.empty:
    nazwisko = st.text_input("Wpisz nazwisko:", "NOWAK").strip().upper()
    
    m_val = st.session_state.df_m[st.session_state.df_m['N'] == nazwisko]['L'].sum()
    f_val = st.session_state.df_z[st.session_state.df_z['N'] == nazwisko]['L'].sum()
    total = m_val + f_val

    st.subheader(f"Wynik dla: {nazwisko}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Suma", f"{total:,}")
    c2.metric("Mężczyźni", f"{m_val:,}")
    c3.metric("Kobiety", f"{f_val:,}")
else:
    st.info("Kliknij przycisk powyżej, aby pobrać dane z serwerów państwowych.")
