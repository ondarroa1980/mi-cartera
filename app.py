import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Mi Cartera MyInvestor", layout="wide")

# --- CARGA DE DATOS REALES DESDE TU EXTRACTO ---
def obtener_historial_inicial():
    # Datos extraídos de tu CSV "Movimientos Mi Cuenta MyInvestor (1).csv"
    return [
        {"Fecha": "2026-01-05", "Ticker": "AMP.MC", "Nombre": "Amper", "Cantidad": 10400.0, "Coste_Total_EUR": 2023.79, "Tipo": "Acción"},
        {"Fecha": "2025-09-22", "Ticker": "NXT.MC", "Nombre": "Nueva Expresión Textil", "Cantidad": 1580.0, "Coste_Total_EUR": 1043.75, "Tipo": "Acción"},
        {"Fecha": "2025-10-09", "Ticker": "NXT.MC", "Nombre": "Nueva Expresión Textil", "Cantidad": 1290.0, "Coste_Total_EUR": 1018.05, "Tipo": "Acción"},
        {"Fecha": "2025-12-16", "Ticker": "UNH", "Nombre": "UnitedHealth Group", "Cantidad": 7.0, "Coste_Total_EUR": 1867.84, "Tipo": "Acción"},
        {"Fecha": "2025-09-16", "Ticker": "JD", "Nombre": "JD.com", "Cantidad": 58.0, "Coste_Total_EUR": 1710.79, "Tipo": "Acción"},
        {"Fecha": "2025-02-13", "Ticker": "IWDA.AS", "Nombre": "MSCI World Index", "Cantidad": 17.0, "Coste_Total_EUR": 6516.20, "Tipo": "Fondo"},
        {"Fecha": "2025-11-05", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cantidad": 6.6, "Coste_Total_EUR": 999.98, "Tipo": "Fondo"}
    ]

try:
    df_historial = pd.read_csv("cartera_v3.csv")
except:
    df_historial = pd.DataFrame(obtener_historial_inicial())
    df_historial.to_csv("cartera_v3.csv", index=False)

# --- CONVERSOR DE MONEDA ---
@st.cache_data(ttl=3600)
def get_rate():
    try:
        return yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
    except: return 1.09

# --- PROCESAMIENTO ---
rate = get_rate()
with st.spinner('Sincronizando con el mercado...'):
    res = []
    for _, row in df_historial.iterrows():
        try:
            tk = yf.Ticker(row['Ticker'])
            p_raw = tk.history(period="1d")["Close"].iloc[-1]
            # Si la moneda es USD (como UNH o JD), convertimos el precio actual a EUR
            is_usd = tk.info.get('currency', 'EUR') == 'USD'
            p_eur = p_raw / rate if is_usd else p_raw
        except:
            # Si falla el precio (fondos), usamos el precio de compra como base
            p_eur = row['Coste_Total_EUR'] / row['Cantidad']
        
        v_actual = p_eur * row['Cantidad']
        res.append({
            "Tipo": row['Tipo'],
            "Nombre": row['Nombre'],
            "Cant.": row['Cantidad'],
            "Inversión": row['Coste_Total_EUR'],
            "Valor Act.": v_actual,
            "Ganancia": v_actual - row['Coste_Total_EUR']
        })
    df_calc = pd.DataFrame(res)

# --- INTERFAZ ---
st.title("🏦 Mi Cartera: Acciones y Fondos")

# Métricas Principales
t_inv = df_calc['Inversión'].sum()
t_val = df_calc['Valor Act.'].sum()
t_gan = t_val - t_inv
c1, c2, c3 = st.columns(3)
c1.metric("Inversión Total", f"{t_inv:,.2f} €")
c2.metric("Valor Actual", f"{t_val:,.2f} €")
c3.metric("Ganancia Total", f"{t_gan:,.2f} €", delta=f"{(t_gan/t_inv*100):.2f}%")

st.divider()

# --- SECCIÓN 1: ACCIONES ---
st.header("📈 Mis Acciones")
df_acc = df_calc[df_calc['Tipo'] == 'Acción']
if not df_acc.empty:
    st.dataframe(df_acc.style.format({"Inversión": "{:.2f} €", "Valor Act.": "{:.2f} €", "Ganancia": "{:.2f} €"}), use_container_width=True)
    st.info(f"Subtotal Acciones: {df_acc['Valor Act.'].sum():,.2f} €")

# --- SECCIÓN 2: FONDOS ---
st.header("🧱 Mis Fondos de Inversión")
df_fon = df_calc[df_calc['Tipo'] == 'Fondo']
if not df_fon.empty:
    st.dataframe(df_fon.style.format({"Inversión": "{:.2f} €", "Valor Act.": "{:.2f} €", "Ganancia": "{:.2f} €"}), use_container_width=True)
    st.info(f"Subtotal Fondos: {df_fon['Valor Act.'].sum():,.2f} €")

# --- AÑADIR NUEVAS ---
with st.expander("➕ Añadir nueva compra al historial"):
    with st.form("new"):
        col1, col2, col3 = st.columns(3)
        ntipo = col1.selectbox("Tipo", ["Acción", "Fondo"])
        ntick = col2.text_input("Ticker (ej: SAN.MC)").upper()
        nnom = col3.text_input("Nombre")
        col4, col5 = st.columns(2)
        ncant = col4.number_input("Cantidad", min_value=0.0)
        ncost = col5.number_input("Coste Total pagado en €", min_value=0.0)
        if st.form_submit_button("Guardar"):
            nueva = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), ntick, nnom, ncant, ncost, ntipo]], 
                                columns=["Fecha", "Ticker", "Nombre", "Cantidad", "Coste_Total_EUR", "Tipo"])
            df_historial = pd.concat([df_historial, nueva], ignore_index=True)
            df_historial.to_csv("cartera_v3.csv", index=False)
            st.rerun()

# --- GRÁFICO ---
st.divider()
st.plotly_chart(px.pie(df_calc, values='Valor Act.', names='Nombre', title="Distribución de mi Patrimonio", hole=0.4), use_container_width=True)
