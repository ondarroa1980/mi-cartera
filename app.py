import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cartera Agirre & Uranga v52", layout="wide")

# --- 2. SISTEMA DE SEGURIDAD (FIXED) ---
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

# --- 3. BASE DE DATOS COMPLETA (RECUPERADA) ---
def cargar_datos_maestros():
    return [
        # --- ACCIONES ---
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.1194, "Moneda": "EUR"},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR"},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Moneda": "EUR"},
        {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 530.00, "Moneda": "USD"},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 35.00, "Moneda": "USD"},
        
        # --- FONDOS RENTA 4 ---
        {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
        {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Moneda": "EUR"},
        {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22, "Moneda": "EUR"},
        
        # --- TODAS LAS ENTRADAS DE NUMANTIA ---
        {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
        
        # --- FONDOS MYINVESTOR ---
        {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"},
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR"}
    ]

# --- 4. GESTIÓN DE DATOS ---
ARCHIVO_CSV = "cartera_ Aguirre_Uranga_v52.csv"
if 'df_cartera' not in st.session_state:
    try:
        # Intentamos cargar el CSV si existe
        st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
    except:
        # Si no existe (o es una versión nueva), cargamos la lista completa de arriba
        st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
        st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

# --- 5. LÓGICA DE NEGOCIO ---
rate = st.session_state.get('rate_sync', 1.09)
df = st.session_state.df_cartera.copy()

# Cálculos
df['Valor Mercado'] = df['P_Act'] * df['Cant']
df['Ganancia (€)'] = df['Valor Mercado'] - df['Coste']
df['Rent. %'] = (df['Ganancia (€)'] / df['Coste'] * 100).fillna(0)

# --- 6. INTERFAZ ---
st.title("🏦 Cartera Agirre & Uranga (v52)")

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
    
    # Agrupamos por activo para que no salgan filas repetidas de Numantia
    res = df_sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({
        'Cant':'sum',
        'Coste':'sum',
        'Valor Mercado':'sum',
        'Ganancia (€)':'sum', 
        'P_Act': 'first'
    }).reset_index()
    
    res['Rent. %'] = (res['Ganancia (€)'] / res['Coste'] * 100)
    res['Ganancia Total'] = res.apply(lambda r: fmt_mon(r['Ganancia (€)'], r['Moneda']), axis=1)
    
    col_map = {'Cant': 'Cant.', 'Coste': 'Invertido', 'Valor Mercado': 'Val. Actual', 'P_Act': 'Precio Unit.'}
    
    if filtro == "Fondo":
        # Para fondos, permitimos editar el precio en la tabla
        res_ed = res.rename(columns=col_map)
        edited = st.data_editor(
            res_ed[['Broker', 'Nombre', 'Cant.', 'Invertido', 'Val. Actual', 'Precio Unit.', 'Ganancia Total', 'Rent. %']],
            use_container_width=True, hide_index=True,
            disabled=['Broker', 'Nombre', 'Cant.', 'Invertido', 'Val. Actual', 'Ganancia Total', 'Rent. %']
        )
        # Si el usuario cambia el precio en la tabla, actualizamos el estado
        for i, row in edited.iterrows():
            st.session_state.df_cartera.loc[st.session_state.df_cartera['Nombre'] == row['Nombre'], 'P_Act'] = row['Precio Unit.']
    else:
        st.dataframe(
            res.rename(columns=col_map)[['Broker', 'Nombre', 'Cant.', 'Invertido', 'Val. Actual', 'Precio Unit.', 'Ganancia Total', 'Rent. %']], 
            use_container_width=True, hide_index=True
        )

mostrar_seccion("Acciones", "Acción")
mostrar_seccion("Fondos de Inversión", "Fondo")

# --- 7. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Panel de Control")
    if st.button("🔄 Actualizar Bolsa"):
        with st.spinner("Actualizando..."):
            try:
                rate_val = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
                st.session_state.rate_sync = rate_val
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                        st.session_state.df_cartera.at[i, 'P_Act'] = p / rate_val if row['Moneda'] == "USD" else p
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Error de conexión")

    if st.button("🔓 Cerrar Sesión"):
        st.session_state["password_correct"] = False
        st.rerun()

st.divider()
st.plotly_chart(px.pie(df, values='Valor Mercado', names='Nombre', title="Distribución por Valor Actual", hole=0.4), use_container_width=True)
