import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Mi Cartera MyInvestor", layout="wide")

# --- 1. FUNCIÓN PARA DATOS INICIALES ---
def inicializar_datos():
    return [
        {"Tipo": "Acción", "Ticker": "AMP.MC", "Nombre": "Amper", "Cantidad": 10400.0, "Inversion": 2023.79, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Ticker": "NXT.MC", "Nombre": "Nueva Expresión Textil", "Cantidad": 2870.0, "Inversion": 2061.80, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Ticker": "UNH", "Nombre": "UnitedHealth Group", "Cantidad": 7.0, "Inversion": 1867.84, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Ticker": "JD", "Nombre": "JD.com", "Cantidad": 58.0, "Inversion": 1710.79, "Precio_Act": 0.0},
        {"Tipo": "Fondo", "Ticker": "F-MSCI", "Nombre": "MSCI World Index", "Cantidad": 17.0, "Inversion": 6516.20, "Precio_Act": 383.30},
        {"Tipo": "Fondo", "Ticker": "F-CHINA", "Nombre": "Pictet China Index", "Cantidad": 6.6, "Inversion": 999.98, "Precio_Act": 151.51}
    ]

# Carga de datos persistente
if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_v5.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(inicializar_datos())

# --- 2. BARRA LATERAL (AÑADIR COMPRAS) ---
with st.sidebar:
    st.header("➕ Añadir Operación")
    with st.form("nuevo_activo"):
        tipo_n = st.selectbox("Tipo", ["Acción", "Fondo"])
        ticker_n = st.text_input("Ticker (ej: SAN.MC, AAPL)").upper()
        nombre_n = st.text_input("Nombre (ej: Santander)")
        cant_n = st.number_input("Cantidad", min_value=0.0)
        inv_n = st.number_input("Inversión Total (€)", min_value=0.0)
        p_act_n = st.number_input("Precio Actual (Opcional)", min_value=0.0)
        
        if st.form_submit_button("Guardar en Cartera"):
            nueva_fila = pd.DataFrame([{
                "Tipo": tipo_n, "Ticker": ticker_n, "Nombre": nombre_n, 
                "Cantidad": cant_n, "Inversion": inv_n, "Precio_Act": p_act_n
            }])
            st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, nueva_fila], ignore_index=True)
            st.session_state.df_cartera.to_csv("cartera_v5.csv", index=False)
            st.success("¡Añadido!")
            st.rerun()

# --- 3. ACTUALIZACIÓN AUTOMÁTICA DE ACCIONES ---
@st.cache_data(ttl=3600)
def fetch_prices(df):
    try:
        rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
    except: rate = 1.09
    
    for i, row in df.iterrows():
        if row['Tipo'] == "Acción":
            try:
                # Buscamos precio actual
                tk = yf.Ticker(row['Ticker'])
                precio = tk.history(period="1d")["Close"].iloc[-1]
                if row['Ticker'] in ['UNH', 'JD']: # Conversión USD a EUR
                    df.at[i, 'Precio_Act'] = precio / rate
                else:
                    df.at[i, 'Precio_Act'] = precio
            except: pass
    return df

if st.button("🔄 Sincronizar con Bolsa"):
    st.session_state.df_cartera = fetch_prices(st.session_state.df_cartera)
    st.session_state.df_cartera.to_csv("cartera_v5.csv", index=False)

# --- 4. SECCIÓN ACCIONES (CON RESUMEN PROPIO) ---
st.title("🏦 Mi Cartera Pro")

st.header("📈 Sección de Acciones")
df_acc = st.session_state.df_cartera[st.session_state.df_cartera['Tipo'] == "Acción"].copy()
df_acc['Valor_Mercado'] = df_acc['Precio_Act'] * df_acc['Cantidad']
df_acc['Ganancia'] = df_acc['Valor_Mercado'] - df_acc['Inversion']

# Métricas específicas de acciones
a_inv = df_acc['Inversion'].sum()
a_val = df_acc['Valor_Mercado'].sum()
a_gan = a_val - a_inv
a_per = (a_gan / a_inv * 100) if a_inv > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("Inversión en Acciones", f"{a_inv:,.2f} €")
c2.metric("Valor Actual", f"{a_val:,.2f} €")
c3.metric("Ganancia/Pérdida", f"{a_gan:,.2f} €", delta=f"{a_per:.2f}%")

st.dataframe(df_acc.style.format({
    "Inversion": "{:.2f} €", "Precio_Act": "{:.3f} €", "Valor_Mercado": "{:.2f} €", "Ganancia": "{:.2f} €"
}), use_container_width=True)

# --- 5. SECCIÓN FONDOS ---
st.header("🧱 Sección de Fondos")
st.info("Haz doble clic en 'Precio_Act' para actualizar el valor liquidativo del fondo.")
df_fon = st.session_state.df_cartera[st.session_state.df_cartera['Tipo'] == "Fondo"].copy()
edited_fon = st.data_editor(df_fon, column_order=("Nombre", "Cantidad", "Inversion", "Precio_Act"), use_container_width=True, key="fondos_editor")

if not edited_fon.equals(df_fon):
    st.session_state.df_cartera.update(edited_fon)
    st.session_state.df_cartera.to_csv("cartera_v5.csv", index=False)
    st.rerun()

# --- 6. RESUMEN TOTAL ---
st.divider()
total_inv = st.session_state.df_cartera['Inversion'].sum()
# Calculamos valor total sumando acciones (auto) y fondos (manual)
total_val_acc = (df_acc['Precio_Act'] * df_acc['Cantidad']).sum()
total_val_fon = (edited_fon['Precio_Act'] * edited_fon['Cantidad']).sum()
total_val = total_val_acc + total_val_fon

st.subheader("🌍 Balance Global de Patrimonio")
st.write(f"Suma de todas tus inversiones: **{total_val:,.2f} €**")
st.plotly_chart(px.pie(names=st.session_state.df_cartera['Nombre'], 
                       values=st.session_state.df_cartera['Inversion'], 
                       hole=0.4, title="Distribución por Inversión Inicial"), use_container_width=True)

if st.button("🚨 Borrar todo y resetear"):
    st.session_state.df_cartera = pd.DataFrame(inicializar_datos())
    st.session_state.df_cartera.to_csv("cartera_v5.csv", index=False)
    st.rerun()
