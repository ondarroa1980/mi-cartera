import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera Total", layout="wide")

# --- 1. CARGA ESTRUCTURADA DE TUS DATOS REALES ---
# Datos MyInvestor (Extracto) + Renta 4 (Plusvalías)
def get_clean_data():
    return [
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.19},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 2870.0, "Coste": 2061.80, "P_Act": 0.71},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World", "Cant": 17.0, "Coste": 6516.20, "P_Act": 383.30},
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51},
        # RENTA 4 (Cifras exactas de tu informe de plusvalías)
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS-FR", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63931.67, "P_Act": 92.86},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI-N", "Nombre": "Evli Nordic Corp", "Cant": 65.3287, "Coste": 10000.00, "P_Act": 160.22},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM-US", "Nombre": "JPM US Short Dur", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "R4-NUM", "Nombre": "Numantia Patrimonio", "Cant": 329.434, "Coste": 7951.82, "P_Act": 25.93}
    ]

# Evitamos session_state complejo para que no de error
df = pd.DataFrame(get_clean_data())

# --- 2. TÍTULO Y MÉTRICAS GLOBALES ---
st.title("🏦 Mi Patrimonio: MyInvestor + Renta 4")

# Cálculo de valores actuales
df['Valor_Total'] = df['P_Act'] * df['Cant']
df['Ganancia'] = df['Valor_Total'] - df['Coste']

total_inv = df['Coste'].sum()
total_val = df['Valor_Total'].sum()
total_gan = total_val - total_inv

c1, c2, c3 = st.columns(3)
c1.metric("Inversión Total", f"{total_inv:,.2f} €")
c2.metric("Valor Patrimonio", f"{total_val:,.2f} €")
c3.metric("Beneficio Total", f"{total_gan:,.2f} €", delta=f"{(total_gan/total_inv*100):.2f}%")

st.divider()

# --- 3. SECCIONES SEPARADAS ---

# SECCIÓN ACCIONES
st.header("📈 Acciones (MyInvestor)")
df_acc = df[df['Tipo'] == "Acción"]
st.table(df_acc[['Nombre', 'Cant', 'Coste', 'P_Act', 'Valor_Total', 'Ganancia']].style.format("{:.2f}"))

# SECCIÓN FONDOS
st.header("🧱 Fondos de Inversión")
st.write("Diferenciados por Broker:")
df_fon = df[df['Tipo'] == "Fondo"]
st.table(df_fon[['Broker', 'Nombre', 'Coste', 'P_Act', 'Valor_Total', 'Ganancia']].style.format("{:.2f}"))

# --- 4. DISTRIBUCIÓN ---
st.divider()
fig = px.pie(df, values='Valor_Total', names='Broker', title="¿Dónde está mi dinero?", hole=0.4)
st.plotly_chart(fig, use_container_width=True)

st.info("Para añadir nuevos activos o cambiar precios, escribe 'reset' en el buscador de la barra lateral (próximamente).")
