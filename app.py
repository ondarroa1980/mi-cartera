import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Mi Cartera MyInvestor", layout="wide")

# --- DATOS REALES DE TU CSV ---
def obtener_datos_limpios():
    return [
        {"Ticker": "AMP.MC", "Nombre": "Amper", "Cantidad": 10400.0, "Coste_Total_EUR": 2023.79, "Tipo": "Acción"},
        {"Ticker": "NXT.MC", "Nombre": "Nueva Expresión Textil", "Cantidad": 2870.0, "Coste_Total_EUR": 2061.80, "Tipo": "Acción"},
        {"Ticker": "UNH", "Nombre": "UnitedHealth Group", "Cantidad": 7.0, "Coste_Total_EUR": 1867.84, "Tipo": "Acción"},
        {"Ticker": "JD", "Nombre": "JD.com", "Cantidad": 58.0, "Coste_Total_EUR": 1710.79, "Tipo": "Acción"},
        # Tickers ajustados para mayor compatibilidad
        {"Ticker": "IWDA.AS", "Nombre": "iShares MSCI World", "Cantidad": 17.0, "Coste_Total_EUR": 6516.20, "Tipo": "Fondo"},
        {"Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cantidad": 6.6, "Coste_Total_EUR": 999.98, "Tipo": "Fondo"}
    ]

# Gestión de archivo local
try:
    df_hist = pd.read_csv("mi_cartera_v4.csv")
except:
    df_hist = pd.DataFrame(obtener_datos_limpios())
    df_hist.to_csv("mi_cartera_v4.csv", index=False)

# --- OBTENER TIPO DE CAMBIO ---
@st.cache_data(ttl=3600)
def get_rate():
    try:
        data = yf.download("EURUSD=X", period="1d", progress=False)
        return data['Close'].iloc[-1]
    except: return 1.09

# --- PROCESAMIENTO ---
rate = get_rate()
with st.spinner('Consultando mercados en tiempo real...'):
    res = []
    for _, row in df_hist.iterrows():
        p_eur = 0
        status = "✅"
        try:
            # Descarga de precio
            tk = yf.download(row['Ticker'], period="1d", interval="1m", progress=False)
            if not tk.empty:
                p_raw = tk['Close'].iloc[-1]
                # Si es una acción de EEUU (UNH o JD), convertimos a EUR
                if row['Ticker'] in ['UNH', 'JD']:
                    p_eur = p_raw / rate
                else:
                    p_eur = p_raw
            else:
                raise ValueError("Vacío")
        except:
            # Si falla, usamos el precio de compra y marcamos aviso
            p_eur = row['Coste_Total_EUR'] / row['Cantidad']
            status = "⚠️ (No carga)"

        v_actual = p_eur * row['Cantidad']
        ganancia = v_actual - row['Coste_Total_EUR']
        
        res.append({
            "Estado": status,
            "Tipo": row['Tipo'],
            "Nombre": row['Nombre'],
            "Inversión": row['Coste_Total_EUR'],
            "Valor Act.": v_actual,
            "Ganancia": ganancia,
            "Rent. %": (ganancia / row['Coste_Total_EUR'] * 100) if row['Coste_Total_EUR'] > 0 else 0
        })
    df_calc = pd.DataFrame(res)

# --- DISEÑO ---
st.title("🏦 Mi Cartera: Acciones y Fondos")

# Métricas en la parte superior
t_inv = df_calc['Inversión'].sum()
t_val = df_calc['Valor Act.'].sum()
t_gan = t_val - t_inv
c1, c2, c3 = st.columns(3)
c1.metric("Inversión Total", f"{t_inv:,.2f} €")
c2.metric("Valor Actual", f"{t_val:,.2f} €")
c3.metric("Ganancia Neta", f"{t_gan:,.2f} €", delta=f"{(t_gan/t_inv*100):.2f}%")

st.divider()

# --- 1. ACCIONES ---
st.header("📈 Acciones")
df_acc = df_calc[df_calc['Tipo'] == 'Acción']
st.dataframe(df_acc.style.format({
    "Inversión": "{:.2f} €", "Valor Act.": "{:.2f} €", "Ganancia": "{:.2f} €", "Rent. %": "{:.2f}%"
}).applymap(lambda x: 'color: red' if isinstance(x, (int, float)) and x < 0 else ('color: green' if isinstance(x, (int, float)) and x > 0 else ''), subset=['Ganancia', 'Rent. %']), 
use_container_width=True)

# --- 2. FONDOS ---
st.header("🧱 Fondos de Inversión")
df_fon = df_calc[df_calc['Tipo'] == 'Fondo']
st.dataframe(df_fon.style.format({
    "Inversión": "{:.2f} €", "Valor Act.": "{:.2f} €", "Ganancia": "{:.2f} €", "Rent. %": "{:.2f}%"
}).applymap(lambda x: 'color: red' if isinstance(x, (int, float)) and x < 0 else ('color: green' if isinstance(x, (int, float)) and x > 0 else ''), subset=['Ganancia', 'Rent. %']), 
use_container_width=True)

# --- GESTIÓN ---
with st.expander("⚙️ Configuración y añadir activos"):
    st.write("Añade activos manualmente o resetea la lista.")
    # Formulario para añadir... (omitido por brevedad, igual que el anterior)
    if st.button("🗑️ Resetear a datos originales"):
        pd.DataFrame(obtener_datos_limpios()).to_csv("mi_cartera_v4.csv", index=False)
        st.rerun()

st.divider()
st.plotly_chart(px.pie(df_calc, values='Valor Act.', names='Nombre', title="Distribución por Valor", hole=0.5), use_container_width=True)
