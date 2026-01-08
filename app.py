import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cartera Agirre & Uranga v51", layout="wide")

# --- 2. SISTEMA DE SEGURIDAD (CORREGIDO) ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

def validar_password():
    if st.session_state["password_input"] == "1234":
        st.session_state["password_correct"] = True
    else:
        st.error("🔑 Contraseña incorrecta")

if not st.session_state["password_correct"]:
    st.title("🔐 Acceso Privado")
    st.text_input("Introduce la clave familiar:", type="password", key="password_input", on_change=validar_password)
    st.info("Introduce la contraseña y pulsa Enter para acceder.")
    st.stop()

# --- 3. BASE DE DATOS MAESTRA ---
def cargar_datos_maestros():
    return [
        # ACCIONES
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR"},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR"},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Moneda": "EUR"},
        {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD"},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50, "Moneda": "USD"},
        # FONDOS
        {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
        {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Moneda": "EUR"},
        {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"},
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR"}
    ]

# --- 4. GESTIÓN DE DATOS ---
ARCHIVO_CSV = "cartera_ Aguirre_Uranga_v51.csv"
if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
    except:
        st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
        st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

# --- 5. LÓGICA DE NEGOCIO ---
rate = st.session_state.get('rate_sync', 1.09)
df = st.session_state.df_cartera.copy()

df['Valor Mercado'] = df['P_Act'] * df['Cant']
df['Ganancia (€)'] = df['Valor Mercado'] - df['Coste']
df['Rentabilidad %'] = (df['Ganancia (€)'] / df['Coste'] * 100).fillna(0)

# --- 6. INTERFAZ ---
st.title("🏦 Cartera Agirre & Uranga (v51)")

# Métricas Principales con nombre "Ganancia"
c1, c2, c3 = st.columns(3)
g_acc = df[df['Tipo'] == 'Acción']['Ganancia (€)'].sum()
g_fon = df[df['Tipo'] == 'Fondo']['Ganancia (€)'].sum()
g_tot = df['Ganancia (€)'].sum()

c1.metric("Ganancia Acciones", f"{g_acc:,.2f} €")
c2.metric("Ganancia Fondos", f"{g_fon:,.2f} €")
c3.metric("Ganancia TOTAL", f"{g_tot:,.2f} €")

st.divider()

def fmt_mon(v, mon):
    if mon == "USD": return f"{v:,.2f} € ({v*rate:,.2f} $)"
    return f"{v:,.2f} €"

def mostrar_seccion(titulo, filtro):
    st.header(f"💼 {titulo}")
    df_sub = df[df['Tipo'] == filtro].copy()
    
    # Agrupar para mostrar totales por activo
    res = df_sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({
        'Cant':'sum',
        'Coste':'sum',
        'Valor Mercado':'sum',
        'Ganancia (€)':'sum', 
        'P_Act': 'first'
    }).reset_index()
    
    res['Rent. %'] = (res['Ganancia (€)'] / res['Coste'] * 100)
    res['Ganancia'] = res.apply(lambda r: fmt_mon(r['Ganancia (€)'], r['Moneda']), axis=1)
    
    # Formateo de tabla
    columnas = {
        'Cant': 'Cant.',
        'Coste': 'Invertido',
        'Valor Mercado': 'Val. Actual',
        'P_Act': 'Precio Unit.'
    }
    
    st.dataframe(
        res.rename(columns=columnas)[['Broker', 'Nombre', 'Cant.', 'Invertido', 'Val. Actual', 'Precio Unit.', 'Ganancia', 'Rent. %']], 
        use_container_width=True, 
        hide_index=True
    )

mostrar_seccion("Acciones", "Acción")
mostrar_seccion("Fondos de Inversión", "Fondo")

# --- 7. BOTÓN DE SINCRONIZACIÓN EN EL SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Panel de Control")
    if st.button("🔄 Actualizar Precios Bolsa"):
        with st.spinner("Conectando con mercados..."):
            try:
                # Actualizar Ratio EUR/USD
                ticker_eurusd = yf.Ticker("EURUSD=X")
                hist_eurusd = ticker_eurusd.history(period="1d")
                if not hist_eurusd.empty:
                    rate = hist_eurusd['Close'].iloc[-1]
                    st.session_state.rate_sync = rate
                
                # Actualizar cada acción
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        ticker = yf.Ticker(row['Ticker'])
                        hist = ticker.history(period="1d")
                        if not hist.empty:
                            p_raw = hist['Close'].iloc[-1]
                            # Si es USD, convertimos a EUR antes de guardar
                            if row['Moneda'] == "USD":
                                st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate
                            else:
                                st.session_state.df_cartera.at[i, 'P_Act'] = p_raw
                
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.success("Precios y divisas actualizados.")
                st.rerun()
            except Exception as e:
                st.error(f"Error en la conexión: {e}")

    if st.button("🔓 Cerrar Sesión"):
        st.session_state["password_correct"] = False
        st.rerun()
