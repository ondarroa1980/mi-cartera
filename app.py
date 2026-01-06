import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera MyInvestor", layout="wide")

# --- 1. DATOS DE PARTIDA (Sacados de tu extracto) ---
def inicializar_datos():
    return [
        {"Tipo": "Acción", "Ticker": "AMP.MC", "Nombre": "Amper", "Cantidad": 10400.0, "Inversion": 2023.79, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Ticker": "NXT.MC", "Nombre": "Nueva Expresión Textil", "Cantidad": 2870.0, "Inversion": 2061.80, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Ticker": "UNH", "Nombre": "UnitedHealth Group", "Cantidad": 7.0, "Inversion": 1867.84, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Ticker": "JD", "Nombre": "JD.com", "Cantidad": 58.0, "Inversion": 1710.79, "Precio_Act": 0.0},
        {"Tipo": "Fondo", "Ticker": "F-MSCI", "Nombre": "MSCI World Index", "Cantidad": 17.0, "Inversion": 6516.20, "Precio_Act": 383.30},
        {"Tipo": "Fondo", "Ticker": "F-CHINA", "Nombre": "Pictet China Index", "Cantidad": 6.6, "Inversion": 999.98, "Precio_Act": 151.51}
    ]

# Cargar o crear el archivo de datos
if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_definitiva.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(inicializar_datos())

# --- 2. OBTENER PRECIOS AUTOMÁTICOS (SOLO ACCIONES) ---
@st.cache_data(ttl=3600)
def actualizar_precios_auto(df):
    rate = 1.0  # Por defecto
    try:
        rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
    except: rate = 1.09

    for i, row in df.iterrows():
        if row['Tipo'] == "Acción":
            try:
                tk = yf.Ticker(row['Ticker'])
                hist = tk.history(period="1d")
                if not hist.empty:
                    precio = hist["Close"].iloc[-1]
                    # Si es USD, pasamos a EUR
                    if row['Ticker'] in ['UNH', 'JD']:
                        df.at[i, 'Precio_Act'] = precio / rate
                    else:
                        df.at[i, 'Precio_Act'] = precio
            except:
                pass # Si falla, mantiene el que tiene
    return df

# Botón para forzar actualización de mercado
if st.button("🔄 Actualizar Precios Acciones"):
    st.session_state.df_cartera = actualizar_precios_auto(st.session_state.df_cartera)
    st.session_state.df_cartera.to_csv("cartera_definitiva.csv", index=False)

# --- 3. INTERFAZ ---
st.title("🏦 Mi Cartera Pro")

# --- SECCIÓN ACCIONES ---
st.header("📈 Acciones (Automático)")
df_acc = st.session_state.df_cartera[st.session_state.df_cartera['Tipo'] == "Acción"].copy()
df_acc['Valor_Mercado'] = df_acc['Precio_Act'] * df_acc['Cantidad']
df_acc['Ganancia'] = df_acc['Valor_Mercado'] - df_acc['Inversion']
df_acc['Rent_%'] = (df_acc['Ganancia'] / df_acc['Inversion']) * 100

st.dataframe(df_acc.style.format({
    "Inversion": "{:.2f} €", "Precio_Act": "{:.3f} €", "Valor_Mercado": "{:.2f} €", "Ganancia": "{:.2f} €", "Rent_%": "{:.2f}%"
}), use_container_width=True)

# --- SECCIÓN FONDOS ---
st.header("🧱 Fondos de Inversión")
st.write("💡 *Como los fondos no cargan bien, edita el 'Precio_Act' manualmente con el valor de la App de MyInvestor:*")

# Tabla editable para fondos
df_fon = st.session_state.df_cartera[st.session_state.df_cartera['Tipo'] == "Fondo"].copy()
edited_df_fon = st.data_editor(df_fon, column_order=("Nombre", "Cantidad", "Inversion", "Precio_Act"), use_container_width=True)

# Actualizar datos si el usuario edita el precio del fondo
if not edited_df_fon.equals(df_fon):
    st.session_state.df_cartera.update(edited_df_fon)
    st.session_state.df_cartera.to_csv("cartera_definitiva.csv", index=False)
    st.rerun()

# Cálculos fondos
df_fon_calc = edited_df_fon.copy()
df_fon_calc['Valor_Mercado'] = df_fon_calc['Precio_Act'] * df_fon_calc['Cantidad']
df_fon_calc['Ganancia'] = df_fon_calc['Valor_Mercado'] - df_fon_calc['Inversion']
df_fon_calc['Rent_%'] = (df_fon_calc['Ganancia'] / df_fon_calc['Inversion']) * 100

st.write("**Resumen Fondos:**")
st.dataframe(df_fon_calc[['Nombre', 'Inversion', 'Valor_Mercado', 'Ganancia', 'Rent_%']].style.format({
    "Inversion": "{:.2f} €", "Valor_Mercado": "{:.2f} €", "Ganancia": "{:.2f} €", "Rent_%": "{:.2f}%"
}), use_container_width=True)

# --- 4. MÉTRICAS TOTALES ---
st.divider()
total_inv = df_acc['Inversion'].sum() + df_fon_calc['Inversion'].sum()
total_val = df_acc['Valor_Mercado'].sum() + df_fon_calc['Valor_Mercado'].sum()
total_gan = total_val - total_inv

c1, c2, c3 = st.columns(3)
c1.metric("Inversión Total", f"{total_inv:,.2f} €")
c2.metric("Valor Actual Cartera", f"{total_val:,.2f} €")
c3.metric("Beneficio Neto", f"{total_gan:,.2f} €", delta=f"{(total_gan/total_inv*100):.2f}%")

# Gráfico
st.plotly_chart(px.pie(names=st.session_state.df_cartera['Nombre'], 
                       values=st.session_state.df_cartera['Precio_Act'] * st.session_state.df_cartera['Cantidad'], 
                       hole=0.4, title="Distribución de mi Dinero"), use_container_width=True)
