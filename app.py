import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Mi Cartera Profesional", layout="wide")

# --- 1. DATOS HISTÓRICOS (Tus archivos MyInvestor y Renta 4) ---
def cargar_datos_base():
    return [
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
        {"Fecha": "2025-12-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
        {"Fecha": "2025-02-13", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World Index", "Cant": 17.0, "Coste": 6516.20, "P_Act": 383.30},
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51},
        {"Fecha": "2025-01-01", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS-FR", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63931.67, "P_Act": 92.86},
        {"Fecha": "2025-01-01", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI-N", "Nombre": "Evli Nordic Corp", "Cant": 65.3287, "Coste": 10000.00, "P_Act": 160.221},
        {"Fecha": "2025-01-01", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM-US", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.026},
        {"Fecha": "2025-01-01", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "R4-NUM", "Nombre": "Numantia Patrimonio", "Cant": 329.434, "Coste": 7951.82, "P_Act": 25.937}
    ]

# Persistencia de datos (cartera_v15.csv)
if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_v15.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(cargar_datos_base())

# --- 2. BARRA LATERAL: AÑADIR ---
with st.sidebar:
    st.header("➕ Añadir Operación")
    with st.form("nuevo_form"):
        tipo = st.selectbox("Tipo", ["Acción", "Fondo"])
        broker = st.selectbox("Broker", ["MyInvestor", "Renta 4"])
        f_compra = st.date_input("Fecha de compra", datetime.now())
        nombre = st.text_input("Nombre del activo")
        ticker = st.text_input("Ticker / ISIN").upper()
        cant = st.number_input("Cantidad", min_value=0.0)
        coste = st.number_input("Inversión Total (€)", min_value=0.0)
        p_act = st.number_input("Precio Actual Unitario (€)", min_value=0.0)
        
        if st.form_submit_button("Guardar en Historial"):
            nueva = pd.DataFrame([{"Fecha": str(f_compra), "Tipo": tipo, "Broker": broker, "Ticker": ticker, "Nombre": nombre, "Cant": cant, "Coste": coste, "P_Act": p_act}])
            st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, nueva], ignore_index=True)
            st.session_state.df_cartera.to_csv("cartera_v15.csv", index=False)
            st.rerun()

# --- 3. CÁLCULOS ---
df = st.session_state.df_cartera.copy()
df['Valor_Actual'] = df['P_Act'] * df['Cant']
df['Beneficio'] = df['Valor_Actual'] - df['Coste']

# Métricas por tipo
b_acc = df[df['Tipo'] == "Acción"]['Beneficio'].sum()
b_fon = df[df['Tipo'] == "Fondo"]['Beneficio'].sum()
b_total = b_acc + b_fon

# --- 4. INTERFAZ ---
st.title("📊 Mi Cartera Global Consolidada")

# Métrica de beneficios triples
m1, m2, m3 = st.columns(3)
m1.metric("Beneficio Acciones", f"{b_acc:,.2f} €")
m2.metric("Beneficio Fondos", f"{b_fon:,.2f} €")
m3.metric("Beneficio Total", f"{b_total:,.2f} €")

st.divider()

# --- SECCIÓN ACCIONES ---
st.header("📈 Detalle por Acciones")
df_acc = df[df['Tipo'] == "Acción"]
for nombre in df_acc['Nombre'].unique():
    sub = df_acc[df_acc['Nombre'] == nombre]
    t_val = sub['Valor_Actual'].sum()
    t_gan = sub['Beneficio'].sum()
    
    with st.expander(f"🛒 {nombre} | Valor: {t_val:,.2f} € | Beneficio: {t_gan:,.2f} €"):
        st.write(f"**Ticker:** {sub['Ticker'].iloc[0]} | **Entidad:** {sub['Broker'].iloc[0]}")
        # Formato seguro: solo columnas numéricas
        cols_mostrar = ['Fecha', 'Cant', 'Coste', 'P_Act', 'Beneficio']
        st.dataframe(sub[cols_mostrar].style.format({
            "Cant": "{:.2f}", "Coste": "{:.2f} €", "P_Act": "{:.3f} €", "Beneficio": "{:.2f} €"
        }), use_container_width=True)

st.divider()

# --- SECCIÓN FONDOS ---
st.header("🧱 Detalle por Fondos")
df_fon = df[df['Tipo'] == "Fondo"]
for ent en ["MyInvestor", "Renta 4"]:
    st.subheader(f"Broker: {ent}")
    sub_fon = df_fon[df_fon['Broker'] == ent]
    if not sub_fon.empty:
        # Editor interactivo para actualizar precios de fondos
        edited = st.data_editor(sub_fon, column_order=("Nombre", "Coste", "P_Act", "Valor_Actual", "Beneficio"), 
                               key=f"editor_{ent}", use_container_width=True)
        if not edited.equals(sub_fon):
            st.session_state.df_cartera.update(edited)
            st.session_state.df_cartera.to_csv("cartera_v15.csv", index=False)
            st.rerun()

# --- 5. GRÁFICO ---
st.divider()
st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', hole=0.4, title="Distribución de mi Patrimonio"), use_container_width=True)

if st.sidebar.button("🚨 Resetear todo"):
    st.session_state.df_cartera = pd.DataFrame(cargar_datos_base())
    st.session_state.df_cartera.to_csv("cartera_v15.csv", index=False)
    st.rerun()
