import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera Consolidada", layout="wide")

# --- 1. DATOS INICIALES (MyInvestor + Renta 4) ---
def get_initial_data():
    return [
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 2870.0, "Coste": 2061.80, "P_Act": 0.718},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World", "Cant": 17.0, "Coste": 6516.20, "P_Act": 383.30},
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS-FR", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63931.67, "P_Act": 92.86},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI-N", "Nombre": "Evli Nordic Corp", "Cant": 65.3287, "Coste": 10000.00, "P_Act": 160.22},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM-US", "Nombre": "JPM US Short Dur", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "R4-NUM", "Nombre": "Numantia Patrimonio", "Cant": 329.434, "Coste": 7951.82, "P_Act": 25.93}
    ]

# Persistencia de datos
if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_final_v12.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(get_initial_data())

# --- 2. BARRA LATERAL: AÑADIR NUEVOS ---
with st.sidebar:
    st.header("➕ Añadir Inversión")
    with st.form("form_nuevo"):
        tipo = st.selectbox("Tipo", ["Acción", "Fondo"])
        broker = st.selectbox("Broker", ["MyInvestor", "Renta 4"])
        nombre = st.text_input("Nombre")
        ticker = st.text_input("Ticker / ISIN").upper()
        cant = st.number_input("Cantidad", min_value=0.0)
        coste = st.number_input("Inversión Total (€)", min_value=0.0)
        p_act = st.number_input("Precio Actual (€)", min_value=0.0)
        if st.form_submit_button("Guardar"):
            nueva = pd.DataFrame([{"Tipo": tipo, "Broker": broker, "Ticker": ticker, "Nombre": nombre, "Cant": cant, "Coste": coste, "P_Act": p_act}])
            st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, nueva], ignore_index=True)
            st.session_state.df_cartera.to_csv("cartera_final_v12.csv", index=False)
            st.rerun()

# --- 3. ACTUALIZAR ACCIONES ---
if st.button("🔄 Actualizar Bolsa"):
    try:
        rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
        for i, row in st.session_state.df_cartera.iterrows():
            if row['Tipo'] == "Acción":
                p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                st.session_state.df_cartera.at[i, 'P_Act'] = p / rate if row['Ticker'] in ['UNH', 'JD'] else p
        st.session_state.df_cartera.to_csv("cartera_final_v12.csv", index=False)
        st.rerun()
    except:
        st.error("Fallo al conectar con Yahoo Finance.")

# --- 4. CÁLCULOS Y TABLAS ---
st.title("🏦 Mi Patrimonio Global")

# Preparar datos para visualización
df = st.session_state.df_cartera.copy()
df['Valor_Actual'] = df['P_Act'] * df['Cant']
df['Ganancia'] = df['Valor_Actual'] - df['Coste']
df['Rent_%'] = (df['Ganancia'] / df['Coste'] * 100).fillna(0)

# Formato numérico seguro (solo para columnas de números)
formatos = {"Cant": "{:.2f}", "Coste": "{:.2f} €", "P_Act": "{:.3f} €", "Valor_Actual": "{:.2f} €", "Ganancia": "{:.2f} €", "Rent_%": "{:.2f}%"}

# SECCIÓN ACCIONES
st.header("📈 Acciones")
df_acc = df[df['Tipo'] == "Acción"]
a_inv, a_val = df_acc['Coste'].sum(), df_acc['Valor_Actual'].sum()
a_gan = a_val - a_inv

col_a1, col_a2, col_a3 = st.columns(3)
col_a1.metric("Inversión Acciones", f"{a_inv:,.2f} €")
col_a2.metric("Valor Actual", f"{a_val:,.2f} €")
col_a3.metric("Beneficio", f"{a_gan:,.2f} €", delta=f"{(a_gan/a_inv*100 if a_inv>0 else 0):.2f}%")

st.dataframe(df_acc[['Nombre', 'Cant', 'Coste', 'P_Act', 'Valor_Actual', 'Ganancia', 'Rent_%']].style.format(formatos), use_container_width=True)

# SECCIÓN FONDOS
st.header("🧱 Fondos de Inversión")
df_fon = df[df['Tipo'] == "Fondo"]
# El editor permite cambiar el precio de los fondos de Renta 4
edited_fon = st.data_editor(df_fon, column_order=("Broker", "Nombre", "Coste", "P_Act"), use_container_width=True)

if not edited_fon.equals(df_fon):
    st.session_state.df_cartera.update(edited_fon)
    st.session_state.df_cartera.to_csv("cartera_final_v12.csv", index=False)
    st.rerun()

# --- 5. PATRIMONIO TOTAL ---
st.divider()
t_inv, t_val = df['Coste'].sum(), (df['P_Act'] * df['Cant']).sum()
st.subheader(f"💰 Patrimonio Total: {t_val:,.2f} €")
st.plotly_chart(px.pie(df, values='Valor_Actual', names='Broker', hole=0.4, title="Distribución por Entidad"), use_container_width=True)

if st.button("🚨 Resetear todo"):
    st.session_state.df_cartera = pd.DataFrame(get_initial_data())
    st.session_state.df_cartera.to_csv("cartera_final_v12.csv", index=False)
    st.rerun()
