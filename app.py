import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Gestor de Inversiones MyInvestor", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 Mi Cartera de Inversiones")

# --- FUNCIONES DE APOYO ---
def get_conversion_rate():
    try:
        return yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
    except:
        return 1.09 # Cambio aproximado si falla la API

def cargar_datos():
    try:
        df = pd.read_csv("cartera.csv")
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        return df
    except:
        return pd.DataFrame(columns=["Fecha", "Ticker", "Nombre", "Cantidad", "Precio_Compra", "Tipo", "Moneda"])

df_raw = cargar_datos()

# --- FORMULARIO LATERAL ---
with st.sidebar:
    st.header("➕ Registrar Operación")
    tipo = st.selectbox("Tipo de Activo", ["Acción", "Fondo"])
    ticker = st.text_input("Ticker (ej: UNH, NXT.MC, AMP.MC)").upper()
    nombre = st.text_input("Nombre del Activo")
    fecha = st.date_input("Fecha de compra", datetime.now())
    cantidad = st.number_input("Cantidad de títulos", min_value=0.0, step=0.1)
    precio = st.number_input("Precio de compra (en su moneda original)", min_value=0.0)
    moneda = st.selectbox("Moneda de la compra", ["EUR", "USD"])
    
    if st.button("Añadir a la Cartera"):
        nueva_fila = pd.DataFrame([[fecha, ticker, nombre, cantidad, precio, tipo, moneda]], 
                                 columns=["Fecha", "Ticker", "Nombre", "Cantidad", "Precio_Compra", "Tipo", "Moneda"])
        df_updated = pd.concat([df_raw, nueva_fila], ignore_index=True)
        df_updated.to_csv("cartera.csv", index=False)
        st.success("Operación registrada")
        st.rerun()

# --- PROCESAMIENTO DE DATOS ---
if not df_raw.empty:
    rate = get_conversion_rate()
    
    with st.spinner('Actualizando precios de mercado...'):
        # 1. Agrupar por Ticker para obtener precios actuales
        unique_tickers = df_raw['Ticker'].unique()
        precios_vivos = {}
        for t in unique_tickers:
            try:
                p = yf.Ticker(t).history(period="1d")["Close"].iloc[-1]
                precios_vivos[t] = p
            except:
                precios_vivos[t] = 0

        # 2. Calcular valores por cada fila
        df_calc = df_raw.copy()
        df_calc['Precio_Actual'] = df_calc['Ticker'].map(precios_vivos)
        
        # Convertir a EUR si la moneda es USD
        def conversion_eur(row, col_name):
            val = row[col_name]
            return val / rate if row['Moneda'] == "USD" else val

        df_calc['Precio_Compra_EUR'] = df_calc.apply(lambda r: conversion_eur(r, 'Precio_Compra'), axis=1)
        df_calc['Precio_Actual_EUR'] = df_calc.apply(lambda r: conversion_eur(r, 'Precio_Actual'), axis=1)
        
        df_calc['Inversion_EUR'] = df_calc['Precio_Compra_EUR'] * df_calc['Cantidad']
        df_calc['Valor_Actual_EUR'] = df_calc['Precio_Actual_EUR'] * df_calc['Cantidad']
        df_calc['Ganancia_EUR'] = df_calc['Valor_Actual_EUR'] - df_calc['Inversion_EUR']

    # --- MÉTRICAS GLOBALES ---
    total_inv = df_calc['Inversion_EUR'].sum()
    total_val = df_calc['Valor_Actual_EUR'].sum()
    total_gan = total_val - total_inv
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Inversión Total", f"{total_inv:,.2f} €")
    m2.metric("Valor Actual", f"{total_val:,.2f} €")
    m3.metric("Ganancia Neta", f"{total_gan:,.2f} €", delta=f"{(total_gan/total_inv*100):.2f}%")

    # --- SECCIONES SEPARADAS ---
    st.divider()
    
    def mostrar_seccion(titulo, tipo_filtro):
        st.subheader(titulo)
        data = df_calc[df_calc['Tipo'] == tipo_filtro]
        if not data.empty:
            # Agrupamos para mostrar resumen por activo
            resumen = data.groupby('Nombre').agg({
                'Cantidad': 'sum',
                'Inversion_EUR': 'sum',
                'Valor_Actual_EUR': 'sum',
                'Ganancia_EUR': 'sum'
            }).reset_index()
            resumen['Rent. %'] = (resumen['Ganancia_EUR'] / resumen['Inversion_EUR']) * 100
            
            st.dataframe(resumen.style.format({
                'Cantidad': '{:.2f}',
                'Inversion_EUR': '{:.2f} €',
                'Valor_Actual_EUR': '{:.2f} €',
                'Ganancia_EUR': '{:.2f} €',
                'Rent. %': '{:.2f}%'
            }), use_container_width=True)
        else:
            st.info(f"No hay {titulo.lower()} registrados.")

    col_left, col_right = st.columns(2)
    with col_left:
        mostrar_seccion("📈 Acciones", "Acción")
    with col_right:
        mostrar_seccion("🧱 Fondos", "Fondo")

    # --- GRÁFICO ---
    st.divider()
    fig = px.pie(df_calc, values='Valor_Actual_EUR', names='Nombre', hole=0.4, title="Distribución de mi Patrimonio")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("🗑️ Borrar todo y empezar de cero"):
        pd.DataFrame(columns=["Fecha", "Ticker", "Nombre", "Cantidad", "Precio_Compra", "Tipo", "Moneda"]).to_csv("cartera.csv", index=False)
        st.rerun()

else:
    st.info("La cartera está vacía. Añade tu primera operación en el menú lateral.")
