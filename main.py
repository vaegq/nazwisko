import streamlit as st
import pandas as pd

st.set_page_config(page_title="Licznik Nazwisk 2025", page_icon="📊")

@st.cache_data
def load_local_data(file_path):
    try:
        # Automatyczne wykrywanie separatora (sep=None) dla plików z gov.pl
        df = pd.read_csv(file_path, sep=None, engine='python', encoding='utf-8-sig')
        
        # Standaryzacja nazw kolumn
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Szukamy kolumny z nazwiskiem i liczbą
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
        st.error(f"Błąd wczytywania pliku {file_path}: {e}")
        return pd.DataFrame()

st.title("📊 Lokalny Licznik Nazwisk 2025")

# Wczytywanie plików z dysku
df_m = load_local_data("meskie.csv")
df_z = load_local_data("zenskie.csv")

if not df_m.empty and not df_z.empty:
    nazwisko = st.text_input("Wpisz nazwisko:", "NOWAK").strip().upper()
    
    if nazwisko:
        m_val = df_m[df_m['N'] == nazwisko]['L'].sum()
        f_val = df_z[df_z['N'] == nazwisko]['L'].sum()
        total = m_val + f_val

        st.divider()
        if total > 0:
            c1, c2, c3 = st.columns(3)
            c1.metric("RAZEM", f"{total:,}")
            c2.metric("Mężczyźni ♂", f"{m_val:,}")
            c3.metric("Kobiety ♀", f"{f_val:,}")
        else:
            st.warning(f"Brak nazwiska '{nazwisko}' w lokalnej bazie.")
        st.divider()
else:
    st.error("Nie znaleziono plików 'meskie.csv' lub 'zenskie.csv' w folderze aplikacji.")
    st.info("Upewnij się, że pliki CSV znajdują się w tym samym folderze co main.py")
