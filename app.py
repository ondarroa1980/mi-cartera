import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera Global", layout="wide")

# --- 1. DATOS CALCULADOS SEGÚN TUS EXCEL (MYINVESTOR + RENTA 4) ---
def get_verified_data():
    return [
        # ACCIONES MYINVESTOR (Basado en extracto MyInvestor)
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 2870.0, "Coste": 2061.80, "P_Act": 0.718},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
        
        # FONDOS MYINVESTOR (Basado en extracto MyInvestor)
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World Index", "Cant": 17.0, "Coste": 6516.20, "P_Act": 383.30},
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51},
        
        # FONDOS RENTA 4 (Costes calculados: Valoración - Beneficio del Excel de plusvalías)
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS-FR", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63931.67, "P_Act": 92.86},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI-N", "Nombre": "Evli Nordic Corp", "Cant": 65.3287, "Coste": 10000.00, "P_Act": 160.221},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM-US", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.026},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "R4-NUM", "Nombre": "Numantia Patrimonio", "Cant": 329.434, "Coste": 7951.82, "P_Act": 25.937}
    ]

# Carga de datos con seguridad
if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_final_v13.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(get_verified_data())

# --- 2. ACTUALIZACIÓN AUTOMÁTICA ---
if st.sidebar.button("🔄 Sincronizar Bolsa"):
    try:
        rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
        for i, row in st.session_state.df_cartera.iterrows():
            if row['Tipo'] == "Acción":
                p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                st.session_state.df_cartera.at[i, 'P_Act'] = p / rate if row['Ticker'] in ['UNH', 'JD'] else p
        st.session_state.df_cartera.to_csv("cartera_final_v13.csv", index=False)
        st.rerun()
    except:
        st.sidebar.error("Error al conectar con el mercado.")

# --- 3. CÁLCULOS GENERALES ---
df = st.session_state.df_cartera.copy()
df['Valor_Actual'] = df['P_Act'] * df['Cant']
df['Beneficio'] = df['Valor_Actual'] - df['Coste']

# Agrupación por tipo para métricas
df_acc = df[df['Tipo'] == "Acción"]
df_fon = df[df['Tipo'] == "Fondo"]

# Totales
b_acc = df_acc['Beneficio'].sum()
b_fon = df_fon['Beneficio'].sum()
b_total = b_acc + b_fon

# --- 4. DISEÑO INTERFAZ ---
st.title("💰 Resumen de Beneficios Patrimoniales")

# MÉTRICAS PRINCIPALES
c1, c2, c3 = st.columns(3)
c1.metric("Beneficio ACCIONES", f"{b_acc:,.2f} €")
c2.metric("Beneficio FONDOS", f"{b_fon:,.2f} €")
c3.metric("BENEFICIO TOTAL", f"{b_total:,.2f} €", delta=f"{((total_val := df['Valor_Actual'].sum()) / (total_inv := df['Coste'].sum()) - 1)*100:.2f}%")

st.divider()

# TABLA ACCIONES
st.header("📈 Detalle de Acciones")
cols_num = ["Cant", "Coste", "P_Act", "Valor_Actual", "Beneficio"]
st.dataframe(df_acc[['Nombre', 'Cant', 'Coste', 'P_Act', 'Valor_Actual', 'Beneficio']].style.format({c: "{:.2f}" for c in cols_num}), use_container_width=True)

# TABLA FONDOS
st.header("🧱 Detalle de Fondos (MyInvestor y Renta 4)")
st.info("💡 Puedes editar 'Coste' o 'P_Act' de tus fondos aquí mismo:")
edited_fon = st.data_editor(df_fon, column_order=("Broker", "Nombre", "Coste", "P_Act", "Valor_Actual", "Beneficio"), use_container_width=True)

if not edited_fon.equals(df_fon):
    st.session_state.df_cartera.update(edited_fon)
    st.session_state.df_cartera.to_csv("cartera_final_v13.csv", index=False)
    st.rerun()

# GRÁFICO DE DISTRIBUCIÓN
st.divider()
st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución por Activo", hole=0.4), use_container_width=True)

if st.sidebar.button("🚨 Resetear Datos"):
    st.session_state.df_cartera = pd.DataFrame(get_verified_data())
    st.session_state.df_cartera.to_csv("cartera_final_v13.csv", index=False)
    st.rerun()
