import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Mi Cartera Consolidada", layout="wide")

# --- 1. CARGA DE DATOS (MYINVESTOR + RENTA 4) ---
def cargar_datos_reales():
    return [
        # ACCIONES MYINVESTOR (Historial desglosado)
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
        {"Fecha": "2025-12-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
        # FONDOS MYINVESTOR
        {"Fecha": "2025-02-13", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World", "Cant": 17.0, "Coste": 6516.20, "P_Act": 383.30},
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51},
        # FONDOS RENTA 4 (Datos exactos de plusvalías)
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS-FR", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63931.67, "P_Act": 92.86},
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI-N", "Nombre": "Evli Nordic Corp", "Cant": 65.3287, "Coste": 10000.00, "P_Act": 160.22},
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM-US", "Nombre": "JPM US Short Dur", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "R4-NUM", "Nombre": "Numantia Patrimonio", "Cant": 329.434, "Coste": 7951.82, "P_Act": 25.93}
    ]

# Nuevo archivo para evitar errores: cartera_v16.csv
if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_v16.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(cargar_datos_reales())

# --- 2. BARRA LATERAL: AÑADIR NUEVOS ---
with st.sidebar:
    st.header("➕ Añadir Inversión")
    with st.form("registro"):
        f_tipo = st.selectbox("Tipo", ["Acción", "Fondo"])
        f_broker = st.selectbox("Broker", ["MyInvestor", "Renta 4"])
        f_fecha = st.date_input("Fecha")
        f_nombre = st.text_input("Nombre")
        f_ticker = st.text_input("Ticker").upper()
        f_cant = st.number_input("Cantidad", min_value=0.0)
        f_coste = st.number_input("Inversión (€)", min_value=0.0)
        f_pact = st.number_input("Precio Act. (€)", min_value=0.0)
        if st.form_submit_button("Guardar"):
            n = pd.DataFrame([{"Fecha": str(f_fecha), "Tipo": f_tipo, "Broker": f_broker, "Ticker": f_ticker, "Nombre": f_nombre, "Cant": f_cant, "Coste": f_coste, "P_Act": f_pact}])
            st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, n], ignore_index=True)
            st.session_state.df_cartera.to_csv("cartera_v16.csv", index=False)
            st.rerun()

# --- 3. CÁLCULOS ---
df = st.session_state.df_cartera.copy()
df['Valor_Actual'] = df['P_Act'] * df['Cant']
df['Beneficio'] = df['Valor_Actual'] - df['Coste']

# Métricas desglosadas
b_acc = df[df['Tipo'] == "Acción"]['Beneficio'].sum()
b_fon = df[df['Tipo'] == "Fondo"]['Beneficio'].sum()
b_total = b_acc + b_fon

# --- 4. INTERFAZ ---
st.title("🏦 Panel de Control de Patrimonio")

# MÉTRICAS TRIPLES
col1, col2, col3 = st.columns(3)
col1.metric("Beneficio Acciones", f"{b_acc:,.2f} €")
col2.metric("Beneficio Fondos", f"{b_fon:,.2f} €")
col3.metric("Beneficio TOTAL", f"{b_total:,.2f} €")

st.divider()

# --- SECCIÓN ACCIONES CON DESPLEGABLES ---
st.header("📈 Detalle por Acciones")
df_acc = df[df['Tipo'] == "Acción"]
for nombre in df_acc['Nombre'].unique():
    sub = df_acc[df_acc['Nombre'] == nombre]
    t_val = sub['Valor_Actual'].sum()
    t_ben = sub['Beneficio'].sum()
    
    with st.expander(f"🛒 {nombre} | Valor: {t_val:,.2f} € | G/P: {t_ben:,.2f} €"):
        st.write(f"**Broker:** {sub['Broker'].iloc[0]} | **Ticker:** {sub['Ticker'].iloc[0]}")
        # Formato manual para evitar errores de tipo texto
        resumen = sub[['Fecha', 'Cant', 'Coste', 'P_Act', 'Beneficio']].copy()
        st.dataframe(resumen.style.format({
            "Cant": "{:.2f}", "Coste": "{:.2f} €", "P_Act": "{:.
