import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera Consolidada", layout="wide")

# --- 1. DATOS REALES (MYINVESTOR + RENTA 4 CON PLUSVALÍAS) ---
def inicializar_datos():
    return [
        # ACCIONES MYINVESTOR
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cantidad": 10400.0, "Inversion": 2023.79, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cantidad": 2870.0, "Inversion": 2061.80, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cantidad": 7.0, "Inversion": 1867.84, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cantidad": 58.0, "Inversion": 1710.79, "Precio_Act": 0.0},
        # FONDOS MYINVESTOR
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "F-MSCI", "Nombre": "MSCI World Index", "Cantidad": 17.0, "Inversion": 6516.20, "Precio_Act": 383.30},
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "F-CHINA", "Nombre": "Pictet China Index", "Cantidad": 6.6, "Inversion": 999.98, "Precio_Act": 151.51},
        # FONDOS RENTA 4 (Cifras exactas de tu informe de plusvalías)
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS-FR", "Nombre": "DWS Floating Rate", "Cantidad": 714.627, "Inversion": 63931.67, "Precio_Act": 92.86},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI-N", "Nombre": "Evli Nordic Corp.", "Cantidad": 65.3287, "Inversion": 10000.00, "Precio_Act": 160.221},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM-US", "Nombre": "JPM US Short Duration", "Cantidad": 87.425, "Inversion": 9999.96, "Precio_Act": 108.026},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "R4-NUM", "Nombre": "Numantia Patrimonio", "Cantidad": 329.434, "Inversion": 7951.82, "Precio_Act": 25.937}
    ]

# Carga de datos
if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_final_v8.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(inicializar_datos())

# --- 2. BARRA LATERAL PARA NUEVAS COMPRAS ---
with st.sidebar:
    st.header("➕ Nueva Operación")
    with st.form("registro"):
        f_tipo = st.selectbox("Tipo", ["Acción", "Fondo"])
        f_broker = st.selectbox("Broker", ["MyInvestor", "Renta 4"])
        f_ticker = st.text_input("Ticker / ISIN").upper()
        f_nombre = st.text_input("Nombre")
        f_cant = st.number_input("Cantidad", min_value=0.0)
        f_inv = st.number_input("Inversión Total (€)", min_value=0.0)
        if st.form_submit_button("Añadir a Cartera"):
            nueva = pd.DataFrame([{"Tipo": f_tipo, "Broker": f_broker, "Ticker": f_ticker, "Nombre": f_nombre, "Cantidad": f_cant, "Inversion": f_inv, "Precio_Act": 0.0}])
            st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, nueva], ignore_index=True)
            st.session_state.df_cartera.to_csv("cartera_final_v8.csv", index=False)
            st.rerun()

# --- 3. ACTUALIZACIÓN DE PRECIOS ---
@st.cache_data(ttl=3600)
def sync_data(df):
    try: rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
    except: rate = 1.09
    for i, row in df.iterrows():
        if row['Tipo'] == "Acción":
            try:
                p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                df.at[i, 'Precio_Act'] = p / rate if row['Ticker'] in ['UNH', 'JD'] else p
            except: pass
    return df

if st.button("🔄 Sincronizar Bolsa (MyInvestor)"):
    st.session_state.df_cartera = sync_data(st.session_state.df_cartera)
    st.session_state.df_cartera.to_csv("cartera_final_v8.csv", index=False)

# --- 4. SECCIÓN ACCIONES ---
st.title("🏦 Centro de Mando Patrimonial")

st.header("📈 Acciones (Automático)")
df_acc = st.session_state.df_cartera[st.session_state.df_cartera['Tipo'] == "Acción"].copy()
df_acc['Valor_Mercado'] = df_acc['Precio_Act'] * df_acc['Cantidad']
df_acc['Beneficio'] = df_acc['Valor_Mercado'] - df_acc['Inversion']

# Métricas Acciones
a_inv, a_val = df_acc['Inversion'].sum(), df_acc['Valor_Mercado'].sum()
a_gan = a_val - a_inv
c1, c2, c3 = st.columns(3)
c1.metric("Inversión en Bolsa", f"{a_inv:,.2f} €")
c2.metric("Valor Actual", f"{a_val:,.2f} €")
c3.metric("G/P Acciones", f"{a_gan:,.2f} €", delta=f"{(a_gan/a_inv*100 if a_inv>0 else 0):.2f}%")

st.dataframe(df_acc[['Nombre', 'Cantidad', 'Inversion', 'Precio_Act', 'Valor_Mercado', 'Beneficio']].style.format("{:.2f}"), use_container_width=True)

# --- 5. SECCIÓN FONDOS ---
st.header("🧱 Fondos de Inversión (MyInvestor & Renta 4)")
st.info("💡 Haz doble clic en 'Precio_Act' para actualizar el valor de tus fondos de Renta 4 hoy.")
df_fon = st.session_state.df_cartera[st.session_state.df_cartera['Tipo'] == "Fondo"].copy()
df_fon['Valor_Mercado'] = df_fon['Precio_Act'] * df_fon['Cantidad']
df_fon['Beneficio'] = df_fon['Valor_Mercado'] - df_fon['Inversion']

# Editor para fondos
edited_fon = st.data_editor(df_fon, column_order=("Broker", "Nombre", "Inversion", "Precio_Act", "Valor_Mercado", "Beneficio"), use_container_width=True)

if not edited_fon.equals(df_fon):
    st.session_state.df_cartera.update(edited_fon)
    st.session_state.df_cartera.to_csv("cartera_final_v8.csv", index=False)
    st.rerun()

# --- 6. RESUMEN GLOBAL ---
st.divider()
total_inv = st.session_state.df_cartera['Inversion'].sum()
total_val = (st.session_state.df_cartera['Precio_Act'] * st.session_state.df_cartera['Cantidad']).sum()

col_glob1, col_glob2 = st.columns(2)
col_glob1.subheader(f"💰 Patrimonio Total: {total_val:,.2f} €")
col_glob1.write(f"Inversión total realizada: **{total_inv:,.2f} €**")

# Gráfico de tarta
with col_glob2:
    fig = px.pie(st.session_state.df_cartera, values='Inversion', names='Broker', hole=0.5, title="Distribución por Entidad")
    st.plotly_chart(fig, use_container_width=True)

if st.button("🚨 Resetear App"):
    st.session_state.df_cartera = pd.DataFrame(inicializar_datos())
    st.session_state.df_cartera.to_csv("cartera_final_v8.csv", index=False)
    st.rerun()
