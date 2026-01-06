import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Mi Cartera MyInvestor Pro", layout="wide")

# --- DATOS INICIALES DEL EXTRACTO ---
def obtener_historial_inicial():
    return [
        {"Fecha": "2026-01-05", "Ticker": "AMP.MC", "Nombre": "Amper", "Cantidad": 10400.0, "Precio_Compra_EUR": 0.1946, "Tipo": "Acción"},
        {"Fecha": "2025-09-22", "Ticker": "NXT.MC", "Nombre": "Nueva Expresión Textil", "Cantidad": 1580.0, "Precio_Compra_EUR": 0.6606, "Tipo": "Acción"},
        {"Fecha": "2025-10-09", "Ticker": "NXT.MC", "Nombre": "Nueva Expresión Textil", "Cantidad": 1290.0, "Precio_Compra_EUR": 0.7892, "Tipo": "Acción"},
        {"Fecha": "2025-12-16", "Ticker": "UNH", "Nombre": "UnitedHealth Group", "Cantidad": 7.0, "Precio_Compra_EUR": 266.834, "Tipo": "Acción"},
        {"Fecha": "2025-09-16", "Ticker": "JD", "Nombre": "JD.com", "Cantidad": 58.0, "Precio_Compra_EUR": 29.496, "Tipo": "Acción"},
        # Fondos (Basado en el coste total dividido por participaciones del CSV)
        {"Fecha": "2025-02-13", "Ticker": "0P00018XAR.F", "Nombre": "MSCI World Index", "Cantidad": 17.0, "Precio_Compra_EUR": 383.305, "Tipo": "Fondo"},
        {"Fecha": "2025-11-05", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cantidad": 6.6, "Precio_Compra_EUR": 151.512, "Tipo": "Fondo"}
    ]

# --- LÓGICA DE ARCHIVOS ---
try:
    df_historial = pd.read_csv("cartera_completa.csv")
except:
    df_historial = pd.DataFrame(obtener_historial_inicial())
    df_historial.to_csv("cartera_completa.csv", index=False)

# --- FUNCIÓN DE CAMBIO DE MONEDA ---
@st.cache_data(ttl=3600)
def get_usd_eur():
    try:
        return yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
    except:
        return 0.93

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("➕ Registrar Compra")
    with st.form("nueva_compra"):
        f_tipo = st.selectbox("Tipo", ["Acción", "Fondo"])
        f_ticker = st.text_input("Ticker (ej: SAN.MC, AAPL)").upper()
        f_nombre = st.text_input("Nombre")
        f_fecha = st.date_input("Fecha")
        f_cant = st.number_input("Cantidad", min_value=0.0)
        f_precio = st.number_input("Precio Compra Unitario (€)", min_value=0.0)
        submit = st.form_submit_button("Añadir al Historial")
        
        if submit:
            nueva = pd.DataFrame([[f_fecha, f_ticker, f_nombre, f_cant, f_precio, f_tipo]], 
                                 columns=["Fecha", "Ticker", "Nombre", "Cantidad", "Precio_Compra_EUR", "Tipo"])
            df_historial = pd.concat([df_historial, nueva], ignore_index=True)
            df_historial.to_csv("cartera_completa.csv", index=False)
            st.rerun()

# --- PROCESAMIENTO ---
rate = get_usd_eur()
tickers_unicos = df_historial['Ticker'].unique()

with st.spinner('Sincronizando con el mercado...'):
    precios_eur = {}
    for t in tickers_unicos:
        try:
            tk = yf.Ticker(t)
            p_raw = tk.history(period="1d")["Close"].iloc[-1]
            # Si la moneda de la accion es USD, convertimos el precio actual a EUR
            cur = tk.info.get('currency', 'EUR')
            precios_eur[t] = p_raw / rate if cur == 'USD' else p_raw
        except:
            precios_eur[t] = 0

    # Cálculos sobre el historial
    df_display = df_historial.copy()
    df_display['Precio Actual (€)'] = df_display['Ticker'].map(precios_eur)
    df_display['Inversión (€)'] = df_display['Cantidad'] * df_display['Precio_Compra_EUR']
    df_display['Valor Actual (€)'] = df_display['Cantidad'] * df_display['Precio Actual (€)']
    df_display['Ganancia (€)'] = df_display['Valor Actual (€)'] - df_display['Inversión (€)']

# --- INTERFAZ ---
st.title("🏦 Mi Cartera Global MyInvestor")

# Métricas Totales
c1, c2, c3 = st.columns(3)
t_inv = df_display['Inversión (€)'].sum()
t_val = df_display['Valor Actual (€)'].sum()
t_gan = t_val - t_inv
c1.metric("Total Invertido", f"{t_inv:,.2f} €")
c2.metric("Valor de Mercado", f"{t_val:,.2f} €")
c3.metric("Ganancia Neta", f"{t_gan:,.2f} €", delta=f"{(t_gan/t_inv*100):.2f}%" if t_inv > 0 else "0%")

st.divider()

# Tabs para organizar
tab1, tab2, tab3 = st.tabs(["📊 Resumen por Activo", "📜 Historial de Compras", "🥧 Distribución"])

with tab1:
    col_acc, col_fon = st.columns(2)
    
    def dibujar_resumen(tipo):
        sub = df_display[df_display['Tipo'] == tipo]
        if not sub.empty:
            res = sub.groupby('Nombre').agg({
                'Cantidad': 'sum',
                'Inversión (€)': 'sum',
                'Valor Actual (€)': 'sum',
                'Ganancia (€)': 'sum'
            })
            res['Rent. %'] = (res['Ganancia (€)'] / res['Inversión (€)']) * 100
            st.dataframe(res.style.format("{:.2f}"), use_container_width=True)

    with col_acc:
        st.subheader("📈 Acciones")
        dibujar_resumen("Acción")
    with col_fon:
        st.subheader("🧱 Fondos")
        dibujar_resumen("Fondo")

with tab2:
    st.subheader("Historial Completo de Operaciones")
    st.write("Aquí puedes ver cada compra individual que has realizado.")
    st.dataframe(df_display.sort_values(by="Fecha", ascending=False), use_container_width=True)

with tab3:
    st.subheader("Análisis de Cartera")
    fig = px.sunburst(df_display, path=['Tipo', 'Nombre'], values='Valor Actual (€)',
                      color='Ganancia (€)', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)

if st.button("🚨 Borrar todo el historial"):
    pd.DataFrame(columns=["Fecha", "Ticker", "Nombre", "Cantidad", "Precio_Compra_EUR", "Tipo"]).to_csv("cartera_completa.csv", index=False)
    st.rerun()
