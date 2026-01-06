import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera Consolidada", layout="wide")

# --- DATOS REALES EXTRAÍDOS DE TUS DOCUMENTOS ---
def datos_iniciales_limpios():
    return [
        # ACCIONES MYINVESTOR
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cantidad": 10400.0, "Inversion": 2023.79, "Precio_Act": 0.194},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cantidad": 2870.0, "Inversion": 2061.80, "Precio_Act": 0.718},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cantidad": 7.0, "Inversion": 1867.84, "Precio_Act": 266.83},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cantidad": 58.0, "Inversion": 1710.79, "Precio_Act": 29.50},
        # FONDOS MYINVESTOR
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World Index", "Cantidad": 17.0, "Inversion": 6516.20, "Precio_Act": 383.30},
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cantidad": 6.6, "Inversion": 999.98, "Precio_Act": 151.51},
        # FONDOS RENTA 4 (Calculados con tus plusvalías: Inversion = Valoración - Beneficio)
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS-FR", "Nombre": "DWS Floating Rate", "Cantidad": 714.627, "Inversion": 63931.67, "Precio_Act": 92.86},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI-N", "Nombre": "Evli Nordic Corp.", "Cantidad": 65.3287, "Inversion": 10000.00, "Precio_Act": 160.22},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM-US", "Nombre": "JPM US Short Duration", "Cantidad": 87.425, "Inversion": 9999.96, "Precio_Act": 108.026},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "R4-NUM", "Nombre": "Numantia Patrimonio", "Cantidad": 329.434, "Inversion": 7951.82, "Precio_Act": 25.937}
    ]

# Nombre de archivo nuevo para forzar limpieza
FILE_NAME = "cartera_v10_final.csv"

if 'df_cartera' not in st.session_state:
    try:
        # Intentamos cargar, pero si las columnas no coinciden, forzamos reinicio
        temp_df = pd.read_csv(FILE_NAME)
        if len(temp_df.columns) != 7: raise ValueError("Estructura antigua")
        st.session_state.df_cartera = temp_df
    except:
        st.session_state.df_cartera = pd.DataFrame(datos_iniciales_limpios())
        st.session_state.df_cartera.to_csv(FILE_NAME, index=False)

# --- INTERFAZ ---
st.title("🏦 Mi Patrimonio: MyInvestor & Renta 4")

# Botón de actualización de bolsa
if st.button("🔄 Sincronizar Bolsa"):
    with st.spinner('Actualizando acciones...'):
        try:
            rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
            for i, row in st.session_state.df_cartera.iterrows():
                if row['Tipo'] == "Acción":
                    p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                    st.session_state.df_cartera.at[i, 'Precio_Act'] = p / rate if row['Ticker'] in ['UNH', 'JD'] else p
            st.session_state.df_cartera.to_csv(FILE_NAME, index=False)
            st.rerun()
        except:
            st.error("Error de conexión con el mercado.")

# --- SECCIONES ---
def mostrar_tabla(titulo, tipo):
    st.header(titulo)
    df = st.session_state.df_cartera[st.session_state.df_cartera['Tipo'] == tipo].copy()
    df['Valor'] = df['Precio_Act'] * df['Cantidad']
    df['Ganancia'] = df['Valor'] - df['Inversion']
    
    if tipo == "Acción":
        st.dataframe(df[['Broker', 'Nombre', 'Inversion', 'Precio_Act', 'Valor', 'Ganancia']].style.format("{:.2f}"), use_container_width=True)
    else:
        st.write("💡 Edita el precio para actualizar tus fondos:")
        edited = st.data_editor(df, column_order=("Broker", "Nombre", "Inversion", "Precio_Act"), use_container_width=True, key=f"editor_{tipo}")
        if not edited.equals(df):
            st.session_state.df_cartera.update(edited)
            st.session_state.df_cartera.to_csv(FILE_NAME, index=False)
            st.rerun()

mostrar_tabla("📈 Acciones", "Acción")
st.divider()
mostrar_tabla("🧱 Fondos de Inversión", "Fondo")

# --- RESUMEN TOTAL ---
st.divider()
total_inv = st.session_state.df_cartera['Inversion'].sum()
total_val = (st.session_state.df_cartera['Precio_Act'] * st.session_state.df_cartera['Cantidad']).sum()
total_gan = total_val - total_inv

c1, c2, c3 = st.columns(3)
c1.metric("Inversión Total", f"{total_inv:,.2f} €")
c2.metric("Valor Patrimonio", f"{total_val:,.2f} €")
c3.metric("Beneficio Neto", f"{total_gan:,.2f} €", delta=f"{(total_gan/total_inv*100):.2f}%")

if st.button("🚨 Resetear todo (Limpieza profunda)"):
    st.session_state.df_cartera = pd.DataFrame(datos_iniciales_limpios())
    st.session_state.df_cartera.to_csv(FILE_NAME, index=False)
    st.rerun()
