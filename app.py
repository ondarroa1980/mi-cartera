import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Mi Cartera Profesional", layout="wide")

# --- 1. BASE DE DATOS DE TRANSACCIONES (Datos extraídos de tus archivos) ---
def get_transaction_history():
    return [
        # ACCIONES MYINVESTOR (Compras individuales)
        {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
        {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
        {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
        {"Fecha": "2025-12-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
        {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
        
        # FONDOS MYINVESTOR
        {"Fecha": "2025-02-13", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World Index", "Cant": 17.0, "Coste": 6516.20, "P_Act": 383.30},
        {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51},
        
        # FONDOS RENTA 4 (Costes calculados de tus plusvalías)
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS-FR", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63931.67, "P_Act": 92.86},
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI-N", "Nombre": "Evli Nordic Corp", "Cant": 65.3287, "Coste": 10000.00, "P_Act": 160.221},
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM-US", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.026},
        {"Fecha": "Varios", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "R4-NUM", "Nombre": "Numantia Patrimonio", "Cant": 329.434, "Coste": 7951.82, "P_Act": 25.937}
    ]

if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_historial_v14.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(get_transaction_history())

# --- 2. BARRA LATERAL: FUNCIÓN DE AÑADIR (RECUPERADA) ---
with st.sidebar:
    st.header("➕ Añadir Inversión")
    with st.form("form_registro"):
        f_tipo = st.selectbox("Tipo", ["Acción", "Fondo"])
        f_broker = st.selectbox("Broker", ["MyInvestor", "Renta 4"])
        f_fecha = st.date_input("Fecha de compra", datetime.now())
        f_ticker = st.text_input("Ticker / ISIN").upper()
        f_nombre = st.text_input("Nombre del producto")
        f_cant = st.number_input("Cantidad", min_value=0.0)
        f_coste = st.number_input("Inversión Total (€)", min_value=0.0)
        f_p_act = st.number_input("Precio Actual Unitario (€)", min_value=0.0)
        
        if st.form_submit_button("Guardar Operación"):
            nueva = pd.DataFrame([{
                "Fecha": str(f_fecha), "Tipo": f_tipo, "Broker": f_broker, 
                "Ticker": f_ticker, "Nombre": f_nombre, "Cant": f_cant, 
                "Coste": f_coste, "P_Act": f_p_act
            }])
            st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, nueva], ignore_index=True)
            st.session_state.df_cartera.to_csv("cartera_historial_v14.csv", index=False)
            st.rerun()

# --- 3. ACTUALIZACIÓN Y CÁLCULOS ---
df = st.session_state.df_cartera.copy()
df['Valor_Actual'] = df['P_Act'] * df['Cant']
df['Beneficio'] = df['Valor_Actual'] - df['Coste']

# Métricas Totales
b_acc = df[df['Tipo'] == "Acción"]['Beneficio'].sum()
b_fon = df[df['Tipo'] == "Fondo"]['Beneficio'].sum()
b_total = b_acc + b_fon

# --- 4. DISEÑO DE LA APP ---
st.title("📊 Mi Cartera Consolidada Profesional")

# MÉTRICAS SUPERIORES
c1, c2, c3 = st.columns(3)
c1.metric("Beneficio Acciones", f"{b_acc:,.2f} €")
c2.metric("Beneficio Fondos", f"{b_fon:,.2f} €")
c3.metric("Beneficio Total Global", f"{b_total:,.2f} €")

st.divider()

# --- SECCIÓN DE ACCIONES ---
st.header("📈 Acciones")
# Agrupamos por nombre para el resumen
df_acc = df[df['Tipo'] == "Acción"]
for nombre in df_acc['Nombre'].unique():
    sub = df_acc[df_acc['Nombre'] == nombre]
    t_cant = sub['Cant'].sum()
    t_coste = sub['Coste'].sum()
    t_val = sub['Valor_Actual'].sum()
    t_gan = sub['Beneficio'].sum()
    
    with st.expander(f"🛒 {nombre} | Total: {t_val:,.2f} € | G/P: {t_gan:,.2f} €"):
        st.write(f"**Ticker:** {sub['Ticker'].iloc[0]} | **Broker:** {sub['Broker'].iloc[0]}")
        # Formato de la tabla interna
        st.table(sub[['Fecha', 'Cant', 'Coste', 'P_Act', 'Beneficio']].style.format({
            "Cant": "{:.2f}", "Coste": "{:.2f} €", "P_Act": "{:.3f} €", "Beneficio": "{:.2f} €"
        }))

st.divider()

# --- SECCIÓN DE FONDOS ---
st.header("🧱 Fondos de Inversión")
df_fon = df[df['Tipo'] == "Fondo"]
# En fondos permitimos edición rápida por si cambian precios
for broker in ["MyInvestor", "Renta 4"]:
    st.subheader(f"Entidad: {broker}")
    sub_fon = df_fon[df_fon['Broker'] == broker]
    if not sub_fon.empty:
        # Usamos editor de datos para permitirte cambiar el precio actual rápidamente
        edited = st.data_editor(sub_fon, column_order=("Nombre", "Coste", "P_Act", "Valor_Actual", "Beneficio"), 
                               key=f"editor_{broker}", use_container_width=True)
        if not edited.equals(sub_fon):
            st.session_state.df_cartera.update(edited)
            st.session_state.df_cartera.to_csv("cartera_historial_v14.csv", index=False)
            st.rerun()

# --- 5. GRÁFICO FINAL ---
st.divider()
st.plotly_chart(px.sunburst(df, path=['Broker', 'Tipo', 'Nombre'], values='Valor_Actual', 
                            title="Distribución Total del Patrimonio", color='Beneficio',
                            color_continuous_scale='RdYlGn'), use_container_width=True)

if st.sidebar.button("🚨 Resetear Historial"):
    st.session_state.df_cartera = pd.DataFrame(get_transaction_history())
    st.session_state.df_cartera.to_csv("cartera_historial_v14.csv", index=False)
    st.rerun()
