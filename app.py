import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Cartera Agirre & Uranga v56", layout="wide")

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

# --- 3. DATOS REALES (LISTA COMPLETA DE COMPRAS) ---
def cargar_datos_reales():
    return [
        # ACCIONES
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.189, "Moneda": "EUR"},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.93, "Moneda": "EUR"},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.93, "Moneda": "EUR"},
        {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 292.70, "Moneda": "USD"},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 24.86, "Moneda": "USD"},
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

ARCHIVO_V56 = "cartera_ Aguirre_Uranga_v56.csv"

if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv(ARCHIVO_V56)
    except:
        st.session_state.df = pd.DataFrame(cargar_datos_reales())
        st.session_state.df.to_csv(ARCHIVO_V56, index=False)

# --- 4. CÁLCULOS ---
rate = st.session_state.get('euro_rate', 1.09)
df_calc = st.session_state.df.copy()
df_calc['Valor Mercado'] = df_calc['P_Act'] * df_calc['Cant']
df_calc['Ganancia (€)'] = df_calc['Valor Mercado'] - df_calc['Coste']
df_calc['Rent. %'] = (df_calc['Ganancia (€)'] / df_calc['Coste'] * 100).fillna(0)

# --- 5. INTERFAZ ---
st.title("🏦 Cartera Agirre & Uranga")

# Métricas Superiores
g_acc = df_calc[df_calc['Tipo'] == 'Acción']['Ganancia (€)'].sum()
g_fon = df_calc[df_calc['Tipo'] == 'Fondo']['Ganancia (€)'].sum()
g_tot = df_calc['Ganancia (€)'].sum()

c1, c2, c3 = st.columns(3)
c1.metric("Ganancia Acciones", f"{g_acc:,.2f} €")
c2.metric("Ganancia Fondos", f"{g_fon:,.2f} €")
c3.metric("Ganancia TOTAL VIVA", f"{g_tot:,.2f} €")

st.divider()

# Tablas de Detalle Completo
def mostrar_tabla_limpia(tipo):
    st.subheader(f"💼 {tipo}s")
    # Filtramos por tipo y mantenemos todas las filas originales
    res = df_calc[df_calc['Tipo'] == tipo].copy()
    
    # Formateamos la columna ganancia para mostrar euros (y dólares si aplica)
    res['Ganancia'] = res.apply(lambda r: f"{r['Ganancia (€)']:,.2f} €" + (f" ({r['Ganancia (€)']*rate:,.2f} $)" if r['Moneda'] == "USD" else ""), axis=1)
    
    # Preparamos las columnas finales
    df_ver = res[['Fecha', 'Broker', 'Nombre', 'Cant', 'Coste', 'Valor Mercado', 'P_Act', 'Ganancia', 'Rent. %']].copy()
    
    # Renombrado seguro para evitar KeyErrors
    df_ver.columns = ['Fecha', 'Broker', 'Nombre', 'Cant.', 'Invertido', 'Val. Act.', 'Precio Unit.', 'Ganancia', 'Rent. %']
    
    st.dataframe(df_ver, use_container_width=True, hide_index=True)

mostrar_tabla_limpia("Acción")
mostrar_tabla_limpia("Fondo")

# --- 6. SIDEBAR (PARA OPCIONES SECUNDARIAS) ---
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
            st.session_state.df.to_csv(ARCHIVO_V56, index=False)
            st.rerun()
        except: st.error("Error de conexión con mercados")
    
    if st.button("♻️ Resetear Datos"):
        st.session_state.df = pd.DataFrame(cargar_datos_reales())
        st.session_state.df.to_csv(ARCHIVO_V56, index=False)
        st.rerun()
    
    if st.button("🔓 Salir"):
        st.session_state["autenticado"] = False
        st.rerun()

st.divider()
st.plotly_chart(px.pie(df_calc, values='Valor Mercado', names='Nombre', title="Reparto de la Cartera", hole=0.4), use_container_width=True)
