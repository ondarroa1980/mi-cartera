import streamlit as st
import pandas as pd
import yfinance as yf

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Cartera Agirre & Uranga v58", layout="wide")

# --- 2. SEGURIDAD ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🔐 Acceso Cartera")
    pwd = st.text_input("Introduce la clave:", type="password")
    if pwd == "1234":
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

# --- 3. BASE DE DATOS MAESTRA (16 OPERACIONES REVISADAS) ---
def cargar_datos():
    return [
        # ACCIONES MYINVESTOR
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.119, "Mon": "EUR"},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Mon": "EUR"},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Mon": "EUR"},
        {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 530.00, "Mon": "USD"},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 35.00, "Mon": "USD"},
        
        # FONDOS RENTA 4
        {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Mon": "EUR"},
        {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Mon": "EUR"},
        {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22, "Mon": "EUR"},
        
        # COMPRAS NUMANTIA
        {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.93, "Mon": "EUR"},
        {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.93, "Mon": "EUR"},
        {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.93, "Mon": "EUR"},
        {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.93, "Mon": "EUR"},
        {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.93, "Mon": "EUR"},
        {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.93, "Mon": "EUR"},
        
        # FONDOS MYINVESTOR
        {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 17.0, "Coste": 6516.20, "P_Act": 412.50, "Mon": "EUR"},
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Mon": "EUR"}
    ]

# Forzamos la actualización de datos para que no use archivos viejos
df = pd.DataFrame(cargar_datos())

# --- 4. CÁLCULOS ---
rate = st.session_state.get('euro_rate', 1.09)
df['Val. Actual'] = df['P_Act'] * df['Cant']
df['Ganancia'] = df['Val. Actual'] - df['Coste']
df['Rent. %'] = (df['Ganancia'] / df['Coste'] * 100).fillna(0)

# --- 5. CABECERA ---
st.title("🏦 Cartera Agirre & Uranga")

c1, c2, c3 = st.columns(3)
t_inv = df['Coste'].sum()
t_val = df['Val. Actual'].sum()
t_gan = t_val - t_inv

c1.metric("Inversión Total", f"{t_inv:,.2f} €")
c2.metric("Valor Actual", f"{t_val:,.2f} €")
c3.metric("Ganancia Total", f"{t_gan:,.2f} €", delta=f"{(t_gan/t_inv*100):.2f}%")

st.divider()

# --- 6. TABLAS CON COLORES ---
def aplicar_estilo(val):
    color = 'red' if val < 0 else 'green'
    return f'color: {color}'

def mostrar_tabla(tipo):
    st.subheader(f"💼 {tipo}s")
    df_temp = df[df['Tipo'] == tipo].copy()
    
    # Seleccionamos columnas útiles
    df_ver = df_temp[['Fecha', 'Broker', 'Nombre', 'Cant', 'Coste', 'Val. Actual', 'P_Act', 'Ganancia', 'Rent. %']]
    
    # Formateo y Estilo
    st.dataframe(
        df_ver.style.format({
            'Cant': '{:.2f}', 'Coste': '{:.2f} €', 'Val. Actual': '{:.2f} €', 
            'P_Act': '{:.4f}', 'Ganancia': '{:.2f} €', 'Rent. %': '{:.2f}%'
        }).applymap(aplicar_estilo, subset=['Ganancia', 'Rent. %']),
        use_container_width=True, hide_index=True
    )

mostrar_tabla("Acción")
mostrar_tabla("Fondo")

# --- 7. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Opciones")
    if st.button("🔄 Sincronizar Bolsa"):
        try:
            r = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
            st.session_state.euro_rate = r
            st.success("Sincronizado")
            st.rerun()
        except: st.error("Error conexión")
    
    if st.button("🔓 Salir"):
        st.session_state["auth"] = False
        st.rerun()
