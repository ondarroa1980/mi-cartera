import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cartera Agirre & Uranga", layout="wide")

# --- 2. SISTEMA DE SEGURIDAD ---
def check_password():
    def password_entered():
        if st.session_state.get("password") == "1234":
            st.session_state["password_correct"] = True
        return st.session_state.get("password_correct", False)

if not st.session_state.get("password_correct"):
    st.title("🔐 Acceso Privado")
    st.text_input("Introduce la clave familiar:", type="password", key="password", on_change=check_password)
    st.stop()

# --- 3. BASE DE DATOS MAESTRA (ACTIVOS VIVOS) ---
def cargar_datos_maestros():
    return [
        # ACCIONES
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR"},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR"},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Moneda": "EUR"},
        {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD"},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50, "Moneda": "USD"},
        # FONDOS RENTA 4
        {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
        {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Moneda": "EUR"},
        {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22, "Moneda": "EUR"},
        {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
        # FONDOS MYINVESTOR
        {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"},
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR"}
    ]

# --- 4. GESTIÓN DE ARCHIVOS ---
ARCHIVO_CSV = "cartera_ Aguirre_Uranga_v48.csv"
if 'df_cartera' not in st.session_state:
    try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
    except:
        st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
        st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

# --- 5. SIDEBAR (CORREGIDO Y SEGURO) ---
with st.sidebar:
    st.header("⚙️ Gestión")
    if st.button("🔄 Sincronizar Bolsa"):
        try:
            rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
            st.session_state.rate_sync = rate
            for i, row in st.session_state.df_cartera.iterrows():
                if row['Tipo'] == "Acción":
                    p_raw = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                    # Solo convertimos si la moneda original es USD
                    st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate if row['Moneda'] == "USD" else p_raw
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.success(f"Sincronizado (1€ = {rate:.4f}$)")
            st.rerun()
        except: st.error("Sin conexión.")

# --- 6. CÁLCULOS ---
rt = st.session_state.get('rate_sync', 1.09)
df = st.session_state.df_cartera.copy()
df = df[df['Nombre'] != "JPM US Short Duration"]

# Sumas exactas
df['Valor Mercado'] = df['P_Act'] * df['Cant']
df['Beneficio (€)'] = df['Valor Mercado'] - df['Coste']
df['Rentabilidad %'] = (df['Beneficio (€)'] / df['Coste'] * 100).fillna(0)

# --- 7. INTERFAZ ---
st.title("🏦 Cartera Agirre & Uranga")

c1, c2, c3 = st.columns(3)
b_acc = df[df['Tipo'] == 'Acción']['Beneficio (€)'].sum()
b_fon = df[df['Tipo'] == 'Fondo']['Beneficio (€)'].sum()
b_tot = df['Beneficio (€)'].sum()

c1.metric("Beneficio Acciones", f"{b_acc:,.2f} €", delta=None)
c2.metric("Beneficio Fondos", f"{b_fon:,.2f} €", delta=None)
c3.metric("Beneficio TOTAL VIVO", f"{b_tot:,.2f} €", delta=f"{b_tot*rt:,.2f} $", delta_color="off")

st.divider()

def fmt_mon(v, mon, d=2):
    if mon == "USD": return f"{v:,.{d}f} € ({v*rt:,.2f} $)"
    return f"{v:,.{d}f} €"

def mostrar_seccion(titulo, filtro):
    st.header(f"💼 {titulo}")
    df_sub = df[df['Tipo'] == filtro].copy()
    
    res = df_sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Valor Mercado':'sum','Beneficio (€)':'sum', 'P_Act': 'first'}).reset_index()
    res['Rentabilidad %'] = (res['Beneficio (€)'] / res['Coste'] * 100)
    res['Precio'] = res.apply(lambda r: fmt_mon(r['P_Act'], r['Moneda'], 4), axis=1)
    res['Beneficio Total'] = res.apply(lambda r: fmt_mon(r['Beneficio (€)'], r['Moneda']), axis=1)
    
    if filtro == "Fondo":
        res_ed = res.rename(columns={'P_Act': 'Precio Actual', 'Cant': 'Cantidad / Part.', 'Coste': 'Dinero Invertido'})
        edited = st.data_editor(
            res_ed[['Broker', 'Nombre', 'Cantidad / Part.', 'Dinero Invertido', 'Valor Mercado', 'Precio Actual', 'Beneficio Total', 'Rentabilidad %']],
            use_container_width=True, hide_index=True,
            disabled=['Broker', 'Nombre', 'Cantidad / Part.', 'Dinero Invertido', 'Valor Mercado', 'Beneficio Total', 'Rentabilidad %']
        )
        for i, row in edited.iterrows():
            st.session_state.df_cartera.loc[st.session_state.df_cartera['Nombre'] == row['Nombre'], 'P_Act'] = row['Precio Actual']
    else:
        st.dataframe(res.rename(columns={'Cant': 'Cant.', 'Coste': 'Invertido'})[['Broker', 'Nombre', 'Cant.', 'Invertido', 'Valor Mercado', 'Precio', 'Beneficio Total', 'Rentabilidad %']], use_container_width=True, hide_index=True)

mostrar_seccion("Acciones", "Acción")
mostrar_seccion("Fondos de Inversión", "Fondo")

st.divider()
st.plotly_chart(px.pie(df, values='Valor Mercado', names='Nombre', title="Distribución de Activos Vivos", hole=0.4), use_container_width=True)
