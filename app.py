import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Cartera Agirre & Uranga v53", layout="wide")

# --- 2. SEGURIDAD ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

def entrar():
    if st.session_state["pass_check"] == "1234":
        st.session_state["autenticado"] = True
    else:
        st.error("Clave incorrecta")

if not st.session_state["autenticado"]:
    st.title("🔐 Acceso Cartera")
    st.text_input("Introduce la clave familiar:", type="password", key="pass_check", on_change=entrar)
    st.stop()

# --- 3. DATOS MAESTROS (TODOS TUS ACTIVOS REVISADOS) ---
def cargar_datos_completos():
    return [
        # ACCIONES
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.1194, "Moneda": "EUR"},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR"},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Moneda": "EUR"},
        {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 530.00, "Moneda": "USD"},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 35.00, "Moneda": "USD"},
        # FONDOS RENTA 4
        {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
        {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Moneda": "EUR"},
        {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22, "Moneda": "EUR"},
        {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.9368, "Moneda": "EUR"},
        {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
        # FONDOS MYINVESTOR
        {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"},
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR"}
    ]

# Usamos un nombre de archivo nuevo para forzar la carga de datos completa
ARCHIVO_V53 = "cartera_ Aguirre_Uranga_v53_total.csv"

if 'df_v53' not in st.session_state:
    try:
        st.session_state.df_v53 = pd.read_csv(ARCHIVO_V53)
    except:
        st.session_state.df_v53 = pd.DataFrame(cargar_datos_completos())
        st.session_state.df_v53.to_csv(ARCHIVO_V53, index=False)

# --- 4. CALCULOS ---
df = st.session_state.df_v53.copy()
rate = st.session_state.get('euro_rate', 1.09)

df['Valor Mercado'] = df['P_Act'] * df['Cant']
df['Ganancia (€)'] = df['Valor Mercado'] - df['Coste']
df['Rent. %'] = (df['Ganancia (€)'] / df['Coste'] * 100).fillna(0)

# --- 5. CABECERA ---
st.title("🏦 Cartera Agirre & Uranga")

g_acc = df[df['Tipo'] == 'Acción']['Ganancia (€)'].sum()
g_fon = df[df['Tipo'] == 'Fondo']['Ganancia (€)'].sum()
g_tot = df['Ganancia (€)'].sum()

c1, c2, c3 = st.columns(3)
c1.metric("Ganancia Acciones", f"{g_acc:,.2f} €")
c2.metric("Ganancia Fondos", f"{g_fon:,.2f} €")
c3.metric("Ganancia TOTAL VIVA", f"{g_tot:,.2f} €")

st.divider()

# --- 6. TABLAS ---
def mostrar_bloque(titulo, tipo_filtro):
    st.header(f"💼 {titulo}")
    subset = df[df['Tipo'] == tipo_filtro]
    
    # Agrupamos por Nombre para consolidar compras (como las de Numantia)
    res = subset.groupby(['Nombre', 'Broker', 'Moneda']).agg({
        'Cant': 'sum',
        'Coste': 'sum',
        'Valor Mercado': 'sum',
        'Ganancia (€)': 'sum',
        'P_Act': 'first'
    }).reset_index()
    
    res['Rent. %'] = (res['Ganancia (€)'] / res['Coste'] * 100)
    
    # Formato moneda para la columna Ganancia
    def fmt(row):
        v = row['Ganancia (€)']
        if row['Moneda'] == "USD": return f"{v:,.2f} € ({v*rate:,.2f} $)"
        return f"{v:,.2f} €"
    
    res['Ganancia'] = res.apply(fmt, axis=1)
    
    # Mostrar tabla
    st.dataframe(
        res.rename(columns={'Cant': 'Cant.', 'Coste': 'Invertido', 'Valor Mercado': 'Valor Act.', 'P_Act': 'Precio Unit.'})
        [['Broker', 'Nombre', 'Cant.', 'Invertido', 'Valor Act.', 'Precio Unit.', 'Ganancia', 'Rent. %']],
        use_container_width=True, hide_index=True
    )

mostrar_bloque("Acciones", "Acción")
mostrar_bloque("Fondos de Inversión", "Fondo")

# --- 7. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Opciones")
    if st.button("🔄 Sincronizar con Bolsa"):
        with st.spinner("Conectando..."):
            try:
                # Actualizar Divisa
                new_rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
                st.session_state.euro_rate = new_rate
                # Actualizar Acciones
                for i, row in st.session_state.df_v53.iterrows():
                    if row['Tipo'] == "Acción":
                        p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                        st.session_state.df_v53.at[i, 'P_Act'] = p / new_rate if row['Moneda'] == "USD" else p
                st.session_state.df_v53.to_csv(ARCHIVO_V53, index=False)
                st.rerun()
            except: st.error("Fallo al conectar con Yahoo Finance")

    if st.button("🗑️ Resetear Datos (Carga Total)"):
        st.session_state.df_v53 = pd.DataFrame(cargar_datos_completos())
        st.session_state.df_v53.to_csv(ARCHIVO_V53, index=False)
        st.rerun()

    if st.button("🔓 Salir"):
        st.session_state["autenticado"] = False
        st.rerun()

st.divider()
st.plotly_chart(px.pie(df, values='Valor Mercado', names='Nombre', title="Reparto de la Cartera", hole=0.4), use_container_width=True)
