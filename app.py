import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Nuestra Cartera Familiar - Inteligente", layout="wide")

# --- 2. SISTEMA DE SEGURIDAD ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "1234":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 Acceso Privado")
        st.text_input("Introduce la clave familiar:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 Acceso Privado")
        st.text_input("Clave incorrecta. Inténtalo de nuevo:", type="password", on_change=password_entered, key="password")
        st.error("😕 Esa no es la clave.")
        return False
    return True

if check_password():
    
    # --- 3. BASE DE DATOS MAESTRA (Con indicador de Moneda) ---
    def cargar_datos_maestros():
        return [
            # ACCIONES (Solo UNH y JD están en USD originalmente)
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Divisa": "EUR"},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Divisa": "EUR"},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Divisa": "EUR"},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Divisa": "USD"},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50, "Divisa": "USD"},
            # FONDOS (Todos en EUR)
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Divisa": "EUR"},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Divisa": "EUR"},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0562247428", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02, "Divisa": "EUR"},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Divisa": "EUR"},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Divisa": "EUR"},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Divisa": "EUR"}
        ]

    ARCHIVO_CSV = "cartera_familiar_v37.csv"
    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    # --- 4. SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            try:
                rate_data = yf.Ticker("EURUSD=X").history(period="1d")
                st.session_state.rate = rate_data["Close"].iloc[-1]
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        p_raw = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                        # Si es USD, Yahoo nos da el precio en $, convertimos a EUR para el cálculo interno
                        st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / st.session_state.rate if row['Divisa'] == "USD" else p_raw
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Error de conexión.")
        
        if st.button("🚨 Reiniciar"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.rerun()

    # --- 5. PROCESAMIENTO ---
    curr_rate = st.session_state.get('rate', 1.09)
    df = st.session_state.df_cartera.copy()
    df['Valor_Actual'] = df['P_Act'] * df['Cant']
    df['GP_EUR'] = df['Valor_Actual'] - df['Coste']
    df['Rent. %'] = (df['GP_EUR'] / df['Coste'] * 100).fillna(0)

    # --- 6. INTERFAZ ---
    st.title("🏦 Cuadro de Mando Patrimonial")

    # Métricas de arriba: Si hay algo en USD en esa categoría, mostramos doble divisa
    c1, c2, c3 = st.columns(3)
    
    def fmt_header(val_eur, tiene_usd):
        return f"{val_eur:,.2f} € ({val_eur*curr_rate:,.2f} $)" if tiene_usd else f"{val_eur:,.2f} €"

    c1.metric("G/P Acciones", fmt_header(df[df['Tipo'] == 'Acción']['GP_EUR'].sum(), True))
    c2.metric("G/P Fondos", fmt_header(df[df['Tipo'] == 'Fondo']['GP_EUR'].sum(), False))
    c3.metric("G/P TOTAL", fmt_header(df['GP_EUR'].sum(), True))
    st.divider()

    # Función para formatear celdas de las tablas de forma selectiva
    def bimoneda_si_toca(val_eur, divisa, decimales=2):
        if divisa == "USD":
            return f"{val_eur:,.{decimales}f} € ({val_eur*curr_rate:,.2f} $)"
        return f"{val_eur:,.{decimales}f} €"

    def mostrar_seccion(titulo, filtro):
        st.header(f"💼 {titulo}")
        df_sub = df[df['Tipo'] == filtro].copy()
        
        if filtro == "Fondo":
            st.warning("💡 **RELLENAR ESTO:** Haz doble clic en 'P_Act' para actualizar el precio del banco.")
        
        # Resumen
        res = df_sub.groupby(['Nombre', 'Broker', 'Divisa']).agg({'Cant':'sum','Coste':'sum','Valor_Actual':'sum','GP_EUR':'sum','P_Act':'first'}).reset_index()
        res['Rent. %'] = (res['GP_EUR'] / res['Coste'] * 100)
        
        # Formateo de columnas
        res['Precio (P_Act)'] = res.apply(lambda r: bimoneda_si_toca(r['P_Act'], r['Divisa'], 4), axis=1)
        res['Ganancia (G/P)'] = res.apply(lambda r: bimoneda_si_toca(r['GP_EUR'], r['Divisa']), axis=1)
        
        st.subheader(f"📊 Situación Actual ({titulo})")
        cols = ['Broker', 'Nombre', 'Cant', 'Coste', 'Valor_Actual', 'Precio (P_Act)', 'Ganancia (G/P)', 'Rent. %']
        st.dataframe(res[cols].style.applymap(
            lambda x: f'background-color: {"#d4edda" if x > 0 else "#f8d7da"}' if isinstance(x, (int, float)) else None, 
            subset=['Ganancia (G/P)', 'Rent. %']
        ).format({"Cant":"{:.2f}","Coste":"{:.2f} €","Valor_Actual":"{:.2f} €","Rent. %":"{:.2f}%"}), use_container_width=True)

        # Historial
        st.subheader(f"📜 Detalle por Fechas ({titulo})")
        for n in df_sub['Nombre'].unique():
            h = df_sub[df_sub['Nombre'] == n].sort_values(by='Fecha', ascending=False).copy()
            h['Precio'] = h.apply(lambda r: bimoneda_si_toca(r['P_Act'], r['Divisa'], 4), axis=1)
            h['Ganancia'] = h.apply(lambda r: bimoneda_si_toca(r['GP_EUR'], r['Divisa']), axis=1)
            with st.expander(f"Ver historial: {n}"):
                st.table(h[['Fecha','Cant','Coste','Precio','Ganancia','Rent. %']].style.applymap(
                    lambda x: f'background-color: {"#d4edda" if x > 0 else "#f8d7da"}' if isinstance(x, (int, float)) else None, 
                    subset=['Ganancia', 'Rent. %']
                ).format({"Cant":"{:.4f}","Coste":"{:.2f} €","Rent. %":"{:.2f}%"}))

    mostrar_seccion("Acciones", "Acción")
    st.divider()
    mostrar_seccion("Fondos de Inversión", "Fondo")

    st.divider()
    st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución del Patrimonio", hole=0.4), use_container_width=True)
