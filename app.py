import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cartera Agirre & Uranga v57", layout="wide")

# --- 2. SEGURIDAD (MÉTODO ESTABLE) ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

def validar():
    if st.session_state["p_input"] == "1234":
        st.session_state["autenticado"] = True
    else:
        st.error("Clave incorrecta")

if not st.session_state["autenticado"]:
    st.title("🔐 Acceso Privado")
    st.text_input("Introduce la clave:", type="password", key="p_input", on_change=validar)
    st.stop()

# --- 3. BASE DE DATOS MAESTRA (TODAS TUS OPERACIONES DETALLADAS) ---
def obtener_datos_completos():
    return [
        # ACCIONES
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.119, "Moneda": "EUR"},
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

# Nombre de archivo nuevo para evitar conflictos con versiones "corruptas"
ARCHIVO_MASTER = "cartera_ Aguirre_Uranga_MASTER_v57.csv"

if 'df_master' not in st.session_state:
    try:
        st.session_state.df_master = pd.read_csv(ARCHIVO_MASTER)
    except:
        st.session_state.df_master = pd.DataFrame(obtener_datos_completos())
        st.session_state.df_master.to_csv(ARCHIVO_MASTER, index=False)

# --- 4. CÁLCULOS ---
rate = st.session_state.get('euro_rate', 1.09)
df = st.session_state.df_master.copy()

df['Valor Mercado'] = df['P_Act'] * df['Cant']
df['Ganancia (€)'] = df['Valor Mercado'] - df['Coste']
df['Rent. %'] = (df['Ganancia (€)'] / df['Coste'] * 100).fillna(0)

# --- 5. CABECERA Y MÉTRICAS ---
st.title("🏦 Mi Cartera: Agirre & Uranga")

c1, c2, c3 = st.columns(3)
g_acc = df[df['Tipo'] == 'Acción']['Ganancia (€)'].sum()
g_fon = df[df['Tipo'] == 'Fondo']['Ganancia (€)'].sum()
g_tot = df['Ganancia (€)'].sum()

c1.metric("Ganancia Acciones", f"{g_acc:,.2f} €")
c2.metric("Ganancia Fondos", f"{g_fon:,.2f} €")
c3.metric("Ganancia TOTAL", f"{g_tot:,.2f} €")

st.divider()

# --- 6. TABLAS (VISTA DETALLADA SIN AGRUPAR) ---
def mostrar_bloque(tipo):
    st.subheader(f"💼 Detalle de {tipo}s")
    subset = df[df['Tipo'] == tipo].copy()
    
    # Formateamos la columna Ganancia (EUR y USD si aplica)
    subset['Ganancia'] = subset.apply(lambda r: f"{r['Ganancia (€)']:,.2f} €" + (f" ({r['Ganancia (€)']*rate:,.2f} $)" if r['Moneda'] == "USD" else ""), axis=1)
    
    # Seleccionamos y renombramos las columnas para que se vea como MyInvestor
    final = subset[['Fecha', 'Broker', 'Nombre', 'Cant', 'Coste', 'Valor Mercado', 'P_Act', 'Ganancia', 'Rent. %']].copy()
    final.columns = ['Fecha', 'Broker', 'Nombre', 'Cant.', 'Invertido', 'Valor Actual', 'Precio Unit.', 'Ganancia', 'Rent. %']
    
    st.dataframe(final, use_container_width=True, hide_index=True)

mostrar_bloque("Acción")
mostrar_bloque("Fondo")

# --- 7. SIDEBAR (BOTONES DE CONTROL) ---
with st.sidebar:
    st.header("⚙️ Herramientas")
    
    if st.button("🔄 Actualizar Precios (Bolsa)"):
        try:
            r = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
            st.session_state.euro_rate = r
            for i, row in st.session_state.df_master.iterrows():
                if row['Tipo'] == "Acción":
                    p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                    st.session_state.df_master.at[i, 'P_Act'] = p / r if row['Moneda'] == "USD" else p
            st.session_state.df_master.to_csv(ARCHIVO_MASTER, index=False)
            st.rerun()
        except: st.error("No se pudo conectar con el mercado")

    if st.button("♻️ Restaurar Datos Originales"):
        st.session_state.df_master = pd.DataFrame(obtener_datos_completos())
        st.session_state.df_master.to_csv(ARCHIVO_MASTER, index=False)
        st.rerun()

    if st.button("🔓 Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()

st.divider()
st.plotly_chart(px.pie(df, values='Valor Mercado', names='Nombre', title="Distribución por Valor de Mercado", hole=0.4), use_container_width=True)
