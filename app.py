import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Cartera Agirre & Uranga v55", layout="wide")

# --- 2. SEGURIDAD ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

def entrar():
    if st.session_state["pass_check"] == "1234":
        st.session_state["autenticado"] = True
    else:
        st.error("🔑 Clave incorrecta")

if not st.session_state["autenticado"]:
    st.title("🔐 Acceso Cartera")
    st.text_input("Introduce la clave familiar:", type="password", key="pass_check", on_change=entrar)
    st.stop()

# --- 3. DATOS MAESTROS ---
def cargar_datos_iniciales():
    return [
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.189, "Moneda": "EUR"},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.93, "Moneda": "EUR"},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.93, "Moneda": "EUR"},
        {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 292.70, "Moneda": "USD"},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 24.86, "Moneda": "USD"},
        {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
        {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Moneda": "EUR"},
        {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22, "Moneda": "EUR"},
        {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"},
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR"}
    ]

ARCHIVO_V55 = "cartera_ Aguirre_Uranga_v55.csv"

if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv(ARCHIVO_V55)
    except:
        st.session_state.df = pd.DataFrame(cargar_datos_iniciales())
        st.session_state.df.to_csv(ARCHIVO_V55, index=False)

# --- 4. CÁLCULOS ---
rate = st.session_state.get('euro_rate', 1.09)
working_df = st.session_state.df.copy()
working_df['Valor Mercado'] = working_df['P_Act'] * working_df['Cant']
working_df['Ganancia (€)'] = working_df['Valor Mercado'] - working_df['Coste']
working_df['Rent. %'] = (working_df['Ganancia (€)'] / working_df['Coste'] * 100).fillna(0)

# --- 5. INTERFAZ ---
st.title("🏦 Cartera Agirre & Uranga")

g_acc = working_df[working_df['Tipo'] == 'Acción']['Ganancia (€)'].sum()
g_fon = working_df[working_df['Tipo'] == 'Fondo']['Ganancia (€)'].sum()
g_tot = working_df['Ganancia (€)'].sum()

c1, c2, c3 = st.columns(3)
c1.metric("Ganancia Acciones", f"{g_acc:,.2f} €")
c2.metric("Ganancia Fondos", f"{g_fon:,.2f} €")
c3.metric("Ganancia TOTAL", f"{g_tot:,.2f} €")

st.divider()

vista = st.radio("🔍 Selecciona el nivel de detalle:", ["Resumen por Activo", "Detalle de Todas las Compras"], horizontal=True)

def mostrar_seccion(tipo):
    subset = working_df[working_df['Tipo'] == tipo]
    if vista == "Resumen por Activo":
        res = subset.groupby(['Nombre', 'Broker', 'Moneda']).agg({
            'Cant': 'sum', 
            'Coste': 'sum', 
            'Valor Mercado': 'sum', 
            'Ganancia (€)': 'sum', 
            'P_Act': 'first'
        }).reset_index()
    else:
        res = subset.copy()
    
    res['Rent. %'] = (res['Ganancia (€)'] / res['Coste'] * 100)
    res['Ganancia'] = res.apply(lambda r: f"{r['Ganancia (€)']:,.2f} €" + (f" ({r['Ganancia (€)']*rate:,.2f} $)" if r['Moneda'] == "USD" else ""), axis=1)
    
    # Nombres de columnas para el usuario
    columnas_map = {
        'Cant': 'Cant.',
        'Coste': 'Invertido',
        'Valor Mercado': 'Val. Act.',
        'P_Act': 'Precio Unit.',
        'Ganancia': 'Ganancia',
        'Rent. %': 'Rent. %'
    }
    
    # Seleccionamos columnas ANTES de renombrar para evitar el KeyError
    cols_a_mostrar = ['Broker', 'Nombre', 'Cant', 'Coste', 'Valor Mercado', 'P_Act', 'Ganancia', 'Rent. %']
    if vista == "Detalle de Todas las Compras":
        cols_a_mostrar.insert(0, 'Fecha')
    
    # Aplicamos selección y luego renombrado
    df_final = res[cols_a_mostrar].rename(columns=columnas_map)
    
    st.dataframe(df_final, use_container_width=True, hide_index=True)

st.subheader("📈 Acciones")
mostrar_seccion("Acción")

st.subheader("🧱 Fondos de Inversión")
mostrar_seccion("Fondo")

# --- 6. GESTIÓN ---
st.divider()
with st.expander("🛠️ Gestión: Añadir Operaciones"):
    with st.form("nuevo"):
        col1, col2, col3, col4 = st.columns(4)
        f_fecha = col1.date_input("Fecha")
        f_tipo = col2.selectbox("Tipo", ["Acción", "Fondo"])
        f_broker = col3.selectbox("Broker", ["MyInvestor", "Renta 4"])
        f_ticker = col4.text_input("Ticker / ISIN")
        f_nombre = col1.text_input("Nombre")
        f_cant = col2.number_input("Cant.", format="%.4f")
        f_coste = col3.number_input("Inversión €", format="%.2f")
        f_moneda = col4.selectbox("Moneda", ["EUR", "USD"])
        
        if st.form_submit_button("✅ Guardar Compra"):
            nueva = {"Fecha": str(f_fecha), "Tipo": f_tipo, "Broker": f_broker, "Ticker": f_ticker, "Nombre": f_nombre, "Cant": f_cant, "Coste": f_coste, "P_Act": 0.0, "Moneda": f_moneda}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([nueva])], ignore_index=True)
            st.session_state.df.to_csv(ARCHIVO_V55, index=False)
            st.rerun()

# --- 7. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Opciones")
    if st.button("🔄 Sincronizar Bolsa"):
        try:
            r = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
            st.session_state.euro_rate = r
            for i, row in st.session_state.df.iterrows():
                if row['Tipo'] == "Acción":
                    p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                    st.session_state.df.at[i, 'P_Act'] = p / r if row['Moneda'] == "USD" else p
            st.session_state.df.to_csv(ARCHIVO_V55, index=False)
            st.rerun()
        except: st.error("Fallo de conexión")
    
    if st.button("♻️ RESET TOTAL"):
        st.session_state.df = pd.DataFrame(cargar_datos_initiales())
        st.session_state.df.to_csv(ARCHIVO_V55, index=False)
        st.rerun()
