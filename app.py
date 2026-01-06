import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Mi Cartera Pro - Colores", layout="wide")

# --- 1. BASE DE DATOS MAESTRA (DESGLOSE COMPLETO) ---
def cargar_datos_maestros():
    return [
        # ACCIONES (MyInvestor)
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
        {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},

        # FONDOS RENTA 4 (Desglose por suscripciones)
        {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86},
        {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22},
        {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22},
        {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0562247428", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
        {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368},
        {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.9368},
        {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.9368},
        {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.9368},
        {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.9368},
        {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.9368},

        # FONDOS MYINVESTOR (Desglose por suscripciones)
        {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 416.395, "Coste": 5016.20, "P_Act": 12.33},
        {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 43.484, "Coste": 500.00, "P_Act": 12.33},
        {"Fecha": "2025-05-01", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 47.216, "Coste": 500.00, "P_Act": 12.33},
        {"Fecha": "2025-08-13", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 42.847, "Coste": 500.00, "P_Act": 12.33},
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51}
    ]

ARCHIVO_CSV = "cartera_v25_colores.csv"

if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
    except:
        st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
        st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

# --- 2. LOGICA DE COLORES ---
def resaltar_gp(val):
    color = '#d4edda' if val > 0 else '#f8d7da' if val < 0 else None
    return f'background-color: {color}'

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    if st.button("🔄 Sincronizar Bolsa"):
        try:
            rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
            for i, row in st.session_state.df_cartera.iterrows():
                if row['Tipo'] == "Acción":
                    p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                    st.session_state.df_cartera.at[i, 'P_Act'] = p / rate if row['Ticker'] in ['UNH', 'JD'] else p
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.rerun()
        except: st.error("Error de red")
    
    if st.button("🚨 Reiniciar Datos"):
        st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
        st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
        st.rerun()

# --- 4. PROCESAMIENTO ---
df = st.session_state.df_cartera.copy()
df['Valor_Actual'] = df['P_Act'] * df['Cant']
df['G/P (€)'] = df['Valor_Actual'] - df['Coste']
df['Rent. %'] = (df['G/P (€)'] / df['Coste'] * 100).fillna(0)

# --- 5. INTERFAZ ---
st.title("🏦 Cuadro de Mando Patrimonial")

c1, c2, c3 = st.columns(3)
c1.metric("G/P Acciones", f"{df[df['Tipo'] == 'Acción']['G/P (€)'].sum():,.2f} €")
c2.metric("G/P Fondos", f"{df[df['Tipo'] == 'Fondo']['G/P (€)'].sum():,.2f} €")
c3.metric("G/P TOTAL GLOBAL", f"{df['G/P (€)'].sum():,.2f} €")

st.divider()

def mostrar_seccion_pro(titulo, filtro_tipo):
    st.header(f"💼 {titulo}")
    df_sub = df[df['Tipo'] == filtro_tipo]
    
    # RESUMEN (Agrupado y con G/P al final)
    resumen = df_sub.groupby(['Nombre', 'Broker']).agg({
        'Cant': 'sum', 'Coste': 'sum', 'Valor_Actual': 'sum', 'G/P (€)': 'sum'
    }).reset_index()
    resumen['Rent. %'] = (resumen['G/P (€)'] / resumen['Coste'] * 100)
    
    st.subheader(f"📊 Situación Actual ({titulo})")
    # Reordenamos columnas para que G/P y % sean las últimas
    cols_res = ['Broker', 'Nombre', 'Cant', 'Coste', 'Valor_Actual', 'G/P (€)', 'Rent. %']
    st.dataframe(resumen[cols_res].style.applymap(resaltar_gp, subset=['G/P (€)', 'Rent. %']).format({
        "Cant": "{:.2f}", "Coste": "{:.2f} €", "Valor_Actual": "{:.2f} €", "G/P (€)": "{:.2f} €", "Rent. %": "{:.2f}%"
    }), use_container_width=True)
    
    # HISTORIAL (Desplegables)
    st.subheader(f"📜 Historial de Operaciones ({titulo})")
    for nombre in df_sub['Nombre'].unique():
        compras = df_sub[df_sub['Nombre'] == nombre].sort_values(by='Fecha', ascending=False)
        with st.expander(f"Ver desglose por fecha: {nombre}"):
            # G/P y Rentabilidad al final
            cols_hist = ['Fecha', 'Cant', 'Coste', 'P_Act', 'G/P (€)', 'Rent. %']
            st.table(compras[cols_hist].style.applymap(resaltar_gp, subset=['G/P (€)', 'Rent. %']).format({
                "Cant": "{:.4f}", "Coste": "{:.2f} €", "P_Act": "{:.4f} €", "G/P (€)": "{:.2f} €", "Rent. %": "{:.2f}%"
            }))

mostrar_seccion_pro("Acciones", "Acción")
st.divider()
mostrar_seccion_pro("Fondos de Inversión", "Fondo")

# --- 6. GRÁFICO ---
st.divider()
st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución de mi Dinero", hole=0.4), use_container_width=True)
