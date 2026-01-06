import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Gestor de Inversiones Pro", layout="wide")

# --- 1. BASE DE DATOS FUSIONADA CON DESGLOSE POR FECHAS ---
def get_detailed_history():
    return [
        # --- ACCIONES (MyInvestor) ---
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
        {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},

        # --- FONDOS RENTA 4 (Desglosado según informe plusvalías) ---
        {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86},
        {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22},
        {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22},
        {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0562247428", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
        
        # Numantia (Desglose del informe detallado + Ajuste reciente)
        {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.93},
        {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.93},
        {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.93},
        {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.93},
        {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.93},
        {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.93}, # Ajuste para total 329

        # --- FONDOS MYINVESTOR ---
        # MSCI World (Desglose informe detallado)
        {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 416.395, "Coste": 5016.20, "P_Act": 12.33},
        {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 43.484, "Coste": 500.00, "P_Act": 12.33},
        {"Fecha": "2025-05-01", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 47.216, "Coste": 500.00, "P_Act": 12.33},
        {"Fecha": "2025-08-13", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 42.847, "Coste": 500.00, "P_Act": 12.33},
        # Pictet
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51}
    ]

if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_detallada_v22.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(get_detailed_history())

# --- 2. BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Gestión")
    if st.button("🔄 Actualizar Bolsa Ahora"):
        try:
            rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
            for i, row in st.session_state.df_cartera.iterrows():
                if row['Tipo'] == "Acción":
                    p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                    st.session_state.df_cartera.at[i, 'P_Act'] = p / rate if row['Ticker'] in ['UNH', 'JD'] else p
            st.session_state.df_cartera.to_csv("cartera_detallada_v22.csv", index=False)
            st.rerun()
        except: st.error("Error al conectar")

    st.divider()
    st.header("➕ Añadir Operación")
    with st.form("registro"):
        f_tipo = st.selectbox("Tipo", ["Acción", "Fondo"])
        f_broker = st.selectbox("Broker", ["MyInvestor", "Renta 4"])
        f_fecha = st.date_input("Fecha")
        f_nombre = st.text_input("Nombre")
        f_ticker = st.text_input("Ticker").upper()
        f_cant = st.number_input("Cantidad", min_value=0.0)
        f_coste = st.number_input("Inversión Total (€)", min_value=0.0)
        f_pact = st.number_input("Precio Act. (€)", min_value=0.0)
        if st.form_submit_button("Guardar"):
            n = pd.DataFrame([{"Fecha": str(f_fecha), "Tipo": f_tipo, "Broker": f_broker, "Ticker": f_ticker, "Nombre": f_nombre, "Cant": f_cant, "Coste": f_coste, "P_Act": f_pact}])
            st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, n], ignore_index=True)
            st.session_state.df_cartera.to_csv("cartera_detallada_v22.csv", index=False)
            st.rerun()

# --- 3. CÁLCULOS ---
df = st.session_state.df_cartera.copy()
df['Valor_Actual'] = df['P_Act'] * df['Cant']
df['Beneficio'] = df['Valor_Actual'] - df['Coste']

# --- 4. INTERFAZ ---
st.title("🏦 Centro de Mando Patrimonial")

c1, c2, c3 = st.columns(3)
c1.metric("G/P Acciones", f"{df[df['Tipo'] == 'Acción']['Beneficio'].sum():,.2f} €")
c2.metric("G/P Fondos", f"{df[df['Tipo'] == 'Fondo']['Beneficio'].sum():,.2f} €")
c3.metric("G/P TOTAL", f"{df['Beneficio'].sum():,.2f} €")

st.divider()

def dibujar_seccion(titulo, tipo_filtro):
    st.header(titulo)
    df_sub = df[df['Tipo'] == tipo_filtro]
    
    # Resumen
    res = df_sub.groupby('Nombre').agg({
        'Cant': 'sum', 'Coste': 'sum', 'Valor_Actual': 'sum', 'Beneficio': 'sum'
    }).reset_index()
    st.subheader(f"📊 Resumen {titulo}")
    st.dataframe(res.style.format({
        "Cant": "{:.2f}", "Coste": "{:.2f} €", "Valor_Actual": "{:.2f} €", "Beneficio": "{:.2f} €"
    }), use_container_width=True)
    
    # Detalles (Desplegables)
    st.subheader(f"🔍 Detalle por Compras ({titulo})")
    for nombre in df_sub['Nombre'].unique():
        detalle = df_sub[df_sub['Nombre'] == nombre]
        with st.expander(f"Historial: {nombre}"):
            st.table(detalle[['Fecha', 'Cant', 'Coste', 'P_Act', 'Beneficio']].style.format({
                "Cant": "{:.4f}", "Coste": "{:.2f} €", "P_Act": "{:.4f} €", "Beneficio": "{:.2f} €"
            }))

dibujar_seccion("Acciones", "Acción")
st.divider()
dibujar_seccion("Fondos de Inversión", "Fondo")

# --- 5. GRÁFICO ---
st.divider()
st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución de mi Patrimonio", hole=0.4), use_container_width=True)

if st.sidebar.button("🚨 Resetear todo"):
    st.session_state.df_cartera = pd.DataFrame(get_detailed_history())
    st.session_state.df_cartera.to_csv("cartera_detallada_v22.csv", index=False)
    st.rerun()
