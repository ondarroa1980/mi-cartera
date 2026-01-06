import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Mi Cartera Consolidada Pro", layout="wide")

# --- 1. DATOS REALES (MYINVESTOR + RENTA 4) ---
def get_verified_history():
    return [
        # ACCIONES MYINVESTOR (Desglose por fechas)
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
        {"Fecha": "2025-12-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
        
        # FONDOS MYINVESTOR
        {"Fecha": "2025-02-13", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World Index", "Cant": 17.0, "Coste": 6516.20, "P_Act": 383.30},
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51},
        
        # FONDOS RENTA 4 (Costes calculados de tus plusvalías: Valoración - Beneficio)
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS-FR", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63931.67, "P_Act": 92.86},
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI-N", "Nombre": "Evli Nordic Corp", "Cant": 65.3287, "Coste": 10000.00, "P_Act": 160.221},
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM-US", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.026},
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "R4-NUM", "Nombre": "Numantia Patrimonio", "Cant": 329.434, "Coste": 7951.82, "P_Act": 25.937}
    ]

# Nuevo archivo para evitar conflictos: cartera_v17.csv
if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_v17.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(get_verified_history())

# --- 2. BARRA LATERAL: AÑADIR OPERACIONES ---
with st.sidebar:
    st.header("➕ Añadir Inversión")
    with st.form("nuevo_activo"):
        f_tipo = st.selectbox("Tipo", ["Acción", "Fondo"])
        f_broker = st.selectbox("Broker", ["MyInvestor", "Renta 4"])
        f_fecha = st.date_input("Fecha de operación")
        f_nombre = st.text_input("Nombre del activo")
        f_ticker = st.text_input("Ticker / ISIN").upper()
        f_cant = st.number_input("Cantidad", min_value=0.0)
        f_coste = st.number_input("Coste Total (€)", min_value=0.0)
        f_p_act = st.number_input("Precio Actual Unitario (€)", min_value=0.0)
        
        if st.form_submit_button("Guardar"):
            nueva_fila = pd.DataFrame([{
                "Fecha": str(f_fecha), "Tipo": f_tipo, "Broker": f_broker, 
                "Ticker": f_ticker, "Nombre": f_nombre, "Cant": f_cant, 
                "Coste": f_coste, "P_Act": f_p_act
            }])
            st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, nueva_fila], ignore_index=True)
            st.session_state.df_cartera.to_csv("cartera_v17.csv", index=False)
            st.rerun()

# --- 3. CÁLCULOS ---
df = st.session_state.df_cartera.copy()
df['Valor_Actual'] = df['P_Act'] * df['Cant']
df['Beneficio'] = df['Valor_Actual'] - df['Coste']

# Desglose de beneficios
b_acc = df[df['Tipo'] == "Acción"]['Beneficio'].sum()
b_fon = df[df['Tipo'] == "Fondo"]['Beneficio'].sum()
b_total = b_acc + b_fon

# --- 4. INTERFAZ PRINCIPAL ---
st.title("💰 Resumen Patrimonial Consolidado")

# Métricas de Beneficio Triple
c1, c2, c3 = st.columns(3)
c1.metric("Beneficio ACCIONES", f"{b_acc:,.2f} €")
c2.metric("Beneficio FONDOS", f"{b_fon:,.2f} €")
c3.metric("BENEFICIO TOTAL", f"{b_total:,.2f} €")

st.divider()

# --- SECCIÓN ACCIONES CON DESPLEGABLES ---
st.header("📈 Detalle por Acciones")
df_acc = df[df['Tipo'] == "Acción"]

for nombre in df_acc['Nombre'].unique():
    sub = df_acc[df_acc['Nombre'] == nombre]
    t_val = sub['Valor_Actual'].sum()
    t_ben = sub['Beneficio'].sum()
    
    # Cada acción tiene su desplegable
    with st.expander(f"🛒 {nombre} | Valor: {t_val:,.2f} € | G/P: {t_ben:,.2f} €"):
        st.write(f"**Ticker:** {sub['Ticker'].iloc[0]} | **Broker:** {sub['Broker'].iloc[0]}")
        
        # Formateamos solo las columnas numéricas para evitar errores de texto
        cols_numericas = ['Cant', 'Coste', 'P_Act', 'Beneficio']
        resumen = sub[['Fecha'] + cols_numericas]
        
        st.dataframe(resumen.style.format({
            "Cant": "{:.2f}", "Coste": "{:.2f} €", "P_Act": "{:.3f} €", "Beneficio": "{:.2f} €"
        }), use_container_width=True)

st.divider()

# --- SECCIÓN FONDOS ---
st.header("🧱 Detalle por Fondos")
df_fon = df[df['Tipo'] == "Fondo"]

# Editor interactivo para actualizar precios actuales
st.info("💡 Haz doble clic en 'P_Act' para actualizar el precio de tus fondos hoy.")
edited_fon = st.data_editor(df_fon, column_order=("Broker", "Nombre", "Coste", "P_Act", "Valor_Actual", "Beneficio"), 
                             key="editor_fondos_v17", use_container_width=True)

if not edited_fon.equals(df_fon):
    st.session_state.df_cartera.update(edited_fon)
    st.session_state.df_cartera.to_csv("cartera_v17.csv", index=False)
    st.rerun()

# --- 5. GRÁFICO DE DISTRIBUCIÓN ---
st.divider()
st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución de mi Patrimonio", hole=0.4), use_container_width=True)

if st.sidebar.button("🚨 Resetear a datos originales"):
    st.session_state.df_cartera = pd.DataFrame(get_verified_history())
    st.session_state.df_cartera.to_csv("cartera_v17.csv", index=False)
    st.rerun()
