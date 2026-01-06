import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Mi Patrimonio Consolidado", layout="wide")

# --- 1. DATOS HISTÓRICOS REALES ---
def get_verified_history():
    return [
        # ACCIONES MYINVESTOR
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
        {"Fecha": "2025-12-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
        # FONDOS MYINVESTOR
        {"Fecha": "2025-02-13", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World Index", "Cant": 17.0, "Coste": 6516.20, "P_Act": 383.30},
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51},
        # FONDOS RENTA 4
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS-FR", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63931.67, "P_Act": 92.86},
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI-N", "Nombre": "Evli Nordic Corp", "Cant": 65.3287, "Coste": 10000.00, "P_Act": 160.221},
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM-US", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.026},
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "R4-NUM", "Nombre": "Numantia Patrimonio", "Cant": 329.434, "Coste": 7951.82, "P_Act": 25.937}
    ]

if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_v19.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(get_verified_history())

# --- 2. BARRA LATERAL: GESTIÓN ---
with st.sidebar:
    st.header("⚙️ Gestión")
    if st.button("🔄 Actualizar Bolsa Ahora"):
        try:
            rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
            for i, row in st.session_state.df_cartera.iterrows():
                if row['Tipo'] == "Acción":
                    p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                    st.session_state.df_cartera.at[i, 'P_Act'] = p / rate if row['Ticker'] in ['UNH', 'JD'] else p
            st.session_state.df_cartera.to_csv("cartera_v19.csv", index=False)
            st.rerun()
        except: st.error("Error al conectar con la bolsa")

    st.divider()
    st.header("➕ Añadir Operación")
    with st.form("registro"):
        f_tipo = st.selectbox("Tipo", ["Acción", "Fondo"])
        f_broker = st.selectbox("Broker", ["MyInvestor", "Renta 4"])
        f_fecha = st.date_input("Fecha")
        f_nombre = st.text_input("Nombre")
        f_ticker = st.text_input("Ticker").upper()
        f_cant = st.number_input("Cantidad", min_value=0.0)
        f_coste = st.number_input("Coste Total (€)", min_value=0.0)
        f_pact = st.number_input("Precio Act. (€)", min_value=0.0)
        if st.form_submit_button("Guardar en Cartera"):
            n = pd.DataFrame([{"Fecha": str(f_fecha), "Tipo": f_tipo, "Broker": f_broker, "Ticker": f_ticker, "Nombre": f_nombre, "Cant": f_cant, "Coste": f_coste, "P_Act": f_pact}])
            st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, n], ignore_index=True)
            st.session_state.df_cartera.to_csv("cartera_v19.csv", index=False)
            st.rerun()

# --- 3. PROCESAMIENTO ---
df = st.session_state.df_cartera.copy()
df['Valor_Actual'] = df['P_Act'] * df['Cant']
df['Beneficio'] = df['Valor_Actual'] - df['Coste']

b_acc = df[df['Tipo'] == "Acción"]['Beneficio'].sum()
b_fon = df[df['Tipo'] == "Fondo"]['Beneficio'].sum()
b_total = b_acc + b_fon

# --- 4. INTERFAZ ---
st.title("🏦 Cuadro de Mando Patrimonial")

# MÉTRICAS TRIPLES
col1, col2, col3 = st.columns(3)
col1.metric("G/P Acciones", f"{b_acc:,.2f} €")
col2.metric("G/P Fondos", f"{b_fon:,.2f} €")
col3.metric("G/P TOTAL GLOBAL", f"{b_total:,.2f} €")

st.divider()

# --- FUNCIÓN PARA DIBUJAR SECCIONES ---
def dibujar_seccion(titulo, tipo_filtro):
    st.header(titulo)
    df_sub = df[df['Tipo'] == tipo_filtro]
    
    # 1. Resumen Agrupado
    resumen = df_sub.groupby('Nombre').agg({
        'Cant': 'sum',
        'Coste': 'sum',
        'Valor_Actual': 'sum',
        'Beneficio': 'sum'
    }).reset_index()
    
    st.subheader(f"📊 Resumen {titulo}")
    st.dataframe(resumen.style.format({
        "Cant": "{:.2f}", "Coste": "{:.2f} €", "Valor_Actual": "{:.2f} €", "Beneficio": "{:.2f} €"
    }), use_container_width=True)
    
    # 2. Desplegable por Operaciones
    st.subheader(f"🔍 Detalle por Compras ({titulo})")
    for nombre in df_sub['Nombre'].unique():
        detalle = df_sub[df_sub['Nombre'] == nombre]
        with st.expander(f"Historial: {nombre}"):
            st.table(detalle[['Fecha', 'Cant', 'Coste', 'P_Act', 'Beneficio']].style.format({
                "Cant": "{:.2f}", "Coste": "{:.2f} €", "P_Act": "{:.3f} €", "Beneficio": "{:.2f} €"
            }))

# --- RENDERIZAR SECCIONES ---
dibujar_seccion("Acciones", "Acción")
st.divider()
dibujar_seccion("Fondos de Inversión", "Fondo")

# --- 5. GRÁFICO Y CIERRE ---
st.divider()
st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución por Activo", hole=0.4), use_container_width=True)

if st.sidebar.button("🚨 Resetear todo"):
    st.session_state.df_cartera = pd.DataFrame(get_verified_history())
    st.session_state.df_cartera.to_csv("cartera_v19.csv", index=False)
    st.rerun()
