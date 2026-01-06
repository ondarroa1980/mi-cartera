import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Mi Patrimonio Consolidado", layout="wide")

# --- 1. BASE DE DATOS INTEGRAL (Cargada desde tu Informe Detallado) ---
def get_verified_history():
    return [
        # --- ACCIONES (MyInvestor) ---
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
        {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},

        # --- FONDOS RENTA 4 ---
        # DWS Floating Rate (Capital vigente tras traspasos)
        {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86},
        # Evli Nordic
        {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22},
        {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22},
        # R4 Numantia
        {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.93},
        {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8299, "Coste": 500.00, "P_Act": 25.93},
        {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.93},
        {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.93},
        {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.93},
        # JPM US Short Duration
        {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0562247428", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},

        # --- FONDOS MYINVESTOR ---
        # MSCI World
        {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World", "Cant": 415.065, "Coste": 5000.00, "P_Act": 12.33},
        {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World", "Cant": 1.33, "Coste": 16.20, "P_Act": 12.33},
        {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World", "Cant": 43.484, "Coste": 500.00, "P_Act": 12.33},
        {"Fecha": "2025-05-01", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World", "Cant": 47.216, "Coste": 500.00, "P_Act": 12.33},
        {"Fecha": "2025-08-13", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World", "Cant": 42.847, "Coste": 500.00, "P_Act": 12.33}
    ]

if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_v20.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(get_verified_history())

# --- 2. GESTIÓN (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Gestión")
    if st.button("🔄 Actualizar Bolsa Ahora"):
        try:
            rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
            for i, row in st.session_state.df_cartera.iterrows():
                if row['Tipo'] == "Acción":
                    p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                    st.session_state.df_cartera.at[i, 'P_Act'] = p / rate if row['Ticker'] in ['UNH', 'JD'] else p
            st.session_state.df_cartera.to_csv("cartera_v20.csv", index=False)
            st.rerun()
        except: st.error("Error de conexión")

    st.divider()
    st.header("➕ Añadir Inversión")
    with st.form("registro"):
        f_tipo = st.selectbox("Tipo", ["Acción", "Fondo"])
        f_broker = st.selectbox("Broker", ["MyInvestor", "Renta 4"])
        f_fecha = st.date_input("Fecha")
        f_nombre = st.text_input("Nombre")
        f_ticker = st.text_input("Ticker / ISIN").upper()
        f_cant = st.number_input("Cantidad", min_value=0.0)
        f_coste = st.number_input("Coste Total (€)", min_value=0.0)
        f_pact = st.number_input("Precio Act. Unitario (€)", min_value=0.0)
        if st.form_submit_button("Guardar"):
            n = pd.DataFrame([{"Fecha": str(f_fecha), "Tipo": f_tipo, "Broker": f_broker, "Ticker": f_ticker, "Nombre": f_nombre, "Cant": f_cant, "Coste": f_coste, "P_Act": f_pact}])
            st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, n], ignore_index=True)
            st.session_state.df_cartera.to_csv("cartera_v20.csv", index=False)
            st.rerun()

# --- 3. PROCESAMIENTO ---
df = st.session_state.df_cartera.copy()
df['Valor_Actual'] = df['P_Act'] * df['Cant']
df['Beneficio'] = df['Valor_Actual'] - df['Coste']

# Cálculo de Beneficios Separados
b_acc = df[df['Tipo'] == "Acción"]['Beneficio'].sum()
b_fon = df[df['Tipo'] == "Fondo"]['Beneficio'].sum()
b_total = b_acc + b_fon

# --- 4. INTERFAZ ---
st.title("🏦 Cuadro de Mando Patrimonial")

# Métrica de Beneficios Triple
m1, m2, m3 = st.columns(3)
m1.metric("G/P ACCIONES", f"{b_acc:,.2f} €")
m2.metric("G/P FONDOS", f"{b_fon:,.2f} €")
m3.metric("G/P TOTAL GLOBAL", f"{b_total:,.2f} €")

st.divider()

def dibujar_bloque(titulo, tipo_filtro):
    st.header(titulo)
    df_sub = df[df['Tipo'] == tipo_filtro]
    
    # 1. Resumen
    res = df_sub.groupby('Nombre').agg({
        'Cant': 'sum', 'Coste': 'sum', 'Valor_Actual': 'sum', 'Beneficio': 'sum'
    }).reset_index()
    st.subheader(f"📊 Resumen {titulo}")
    st.dataframe(res.style.format({
        "Cant": "{:.2f}", "Coste": "{:.2f} €", "Valor_Actual": "{:.2f} €", "Beneficio": "{:.2f} €"
    }), use_container_width=True)
    
    # 2. Detalles Desplegables
    st.subheader(f"🔍 Detalle por Operaciones ({titulo})")
    for nombre in df_sub['Nombre'].unique():
        detalle = df_sub[df_sub['Nombre'] == nombre]
        with st.expander(f"Historial: {nombre} | ISIN: {detalle['Ticker'].iloc[0]}"):
            st.table(detalle[['Fecha', 'Cant', 'Coste', 'P_Act', 'Beneficio']].style.format({
                "Cant": "{:.4f}", "Coste": "{:.2f} €", "P_Act": "{:.4f} €", "Beneficio": "{:.2f} €"
            }))

# RENDER
dibujar_bloque("Acciones", "Acción")
st.divider()
dibujar_bloque("Fondos de Inversión", "Fondo")

# --- 5. GRÁFICO ---
st.divider()
fig = px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución por Activo", hole=0.4)
st.plotly_chart(fig, use_container_width=True)

if st.sidebar.button("🚨 Resetear todo"):
    st.session_state.df_cartera = pd.DataFrame(get_verified_history())
    st.session_state.df_cartera.to_csv("cartera_v20.csv", index=False)
    st.rerun()
