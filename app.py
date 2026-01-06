import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera Consolidada", layout="wide")

# --- DATOS REALES CORREGIDOS (MyInvestor + Renta 4) ---
def inicializar_datos():
    return [
        # ACCIONES MYINVESTOR
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cantidad": 10400.0, "Inversion": 2023.79, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cantidad": 2870.0, "Inversion": 2061.80, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cantidad": 7.0, "Inversion": 1867.84, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cantidad": 58.0, "Inversion": 1710.79, "Precio_Act": 0.0},
        # FONDOS MYINVESTOR
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World Index", "Cantidad": 17.0, "Inversion": 6516.20, "Precio_Act": 383.30},
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cantidad": 6.6, "Inversion": 999.98, "Precio_Act": 151.51},
        # FONDOS RENTA 4 (Cifras exactas de tu informe)
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS-FR", "Nombre": "DWS Floating Rate", "Cantidad": 714.627, "Inversion": 63931.67, "Precio_Act": 92.86},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI-N", "Nombre": "Evli Nordic Corp.", "Cantidad": 65.3287, "Inversion": 10000.00, "Precio_Act": 160.22},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM-US", "Nombre": "JPM US Short Duration", "Cantidad": 87.425, "Inversion": 9999.96, "Precio_Act": 108.026},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "R4-NUM", "Nombre": "Numantia Patrimonio", "Cantidad": 329.434, "Inversion": 7951.82, "Precio_Act": 25.937}
    ]

# Usamos un nombre de archivo NUEVO para evitar errores: 'datos_v9.csv'
if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("datos_v9.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(inicializar_datos())

# --- INTERFAZ ---
st.title("🏦 Mi Patrimonio Global")

# Botón para actualizar acciones
if st.button("🔄 Actualizar Acciones"):
    try:
        rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
        for i, row in st.session_state.df_cartera.iterrows():
            if row['Tipo'] == "Acción":
                p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                st.session_state.df_cartera.at[i, 'Precio_Act'] = p / rate if row['Ticker'] in ['UNH', 'JD'] else p
        st.session_state.df_cartera.to_csv("datos_v9.csv", index=False)
        st.rerun()
    except:
        st.error("Error al conectar con la bolsa. Inténtalo en unos minutos.")

# TABLA ACCIONES
st.header("📈 Mis Acciones")
df_acc = st.session_state.df_cartera[st.session_state.df_cartera['Tipo'] == "Acción"].copy()
df_acc['Valor'] = df_acc['Precio_Act'] * df_acc['Cantidad']
df_acc['Ganancia'] = df_acc['Valor'] - df_acc['Inversion']
st.dataframe(df_acc.style.format("{:.2f}"), use_container_width=True)

# TABLA FONDOS (Editable)
st.header("🧱 Mis Fondos (MyInvestor y Renta 4)")
st.write("💡 Edita el precio actual de tus fondos si ha cambiado:")
df_fon = st.session_state.df_cartera[st.session_state.df_cartera['Tipo'] == "Fondo"].copy()
df_fon['Valor'] = df_fon['Precio_Act'] * df_fon['Cantidad']
df_fon['Ganancia'] = df_fon['Valor'] - df_fon['Inversion']

edited_fon = st.data_editor(df_fon, column_order=("Broker", "Nombre", "Inversion", "Precio_Act", "Valor", "Ganancia"), use_container_width=True)

if not edited_fon.equals(df_fon):
    st.session_state.df_cartera.update(edited_fon)
    st.session_state.df_cartera.to_csv("datos_v9.csv", index=False)
    st.rerun()

# RESUMEN TOTAL
st.divider()
total_inv = st.session_state.df_cartera['Inversion'].sum()
total_val = (st.session_state.df_cartera['Precio_Act'] * st.session_state.df_cartera['Cantidad']).sum()
st.metric("PATRIMONIO TOTAL ACTUAL", f"{total_val:,.2f} €", delta=f"{(total_val - total_inv):,.2f} €")
