import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Nuestra Cartera Familiar - Bimoneda", layout="wide")

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
    
    # --- 3. BASE DE DATOS MAESTRA ---
    def cargar_datos_maestros():
        return [
            # ACCIONES
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
            # FONDOS
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0562247428", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51}
        ]

    ARCHIVO_CSV = "cartera_familiar_v36.csv"
    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    # --- 4. SIDEBAR (Sync cambio USD) ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            try:
                rate_data = yf.Ticker("EURUSD=X").history(period="1d")
                st.session_state.cambio_usd = rate_data["Close"].iloc[-1]
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        p_raw = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                        # Si es ticker de USA (sin .MC), el precio viene en USD, convertimos a EUR
                        st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / st.session_state.cambio_usd if row['Ticker'] in ['UNH', 'JD'] else p_raw
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Error de sincronización.")
        
        if st.button("🚨 Reiniciar"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.rerun()

    # --- 5. PROCESAMIENTO ---
    rate = st.session_state.get('cambio_usd', 1.09) # Valor estimado si no hay sync
    df = st.session_state.df_cartera.copy()
    df['Valor_Actual'] = df['P_Act'] * df['Cant']
    df['GP_EUR'] = df['Valor_Actual'] - df['Coste']
    df['GP_USD'] = df['GP_EUR'] * rate
    df['Rent. %'] = (df['GP_EUR'] / df['Coste'] * 100).fillna(0)

    # --- 6. INTERFAZ ---
    st.title("🏦 Cuadro de Mando Patrimonial")

    # Métricas principales con doble divisa
    c1, c2, c3 = st.columns(3)
    gp_acc = df[df['Tipo'] == 'Acción']['GP_EUR'].sum()
    gp_fon = df[df['Tipo'] == 'Fondo']['GP_EUR'].sum()
    gp_tot = df['GP_EUR'].sum()

    c1.metric("G/P Acciones", f"{gp_acc:,.2f} € ({gp_acc*rate:,.2f} $)")
    c2.metric("G/P Fondos", f"{gp_fon:,.2f} € ({gp_fon*rate:,.2f} $)")
    c3.metric("G/P TOTAL GLOBAL", f"{gp_tot:,.2f} € ({gp_tot*rate:,.2f} $)")
    st.divider()

    # Función de formateo para las tablas
    def fmt_bimoneda(val_eur):
        return f"{val_eur:,.2f} € ({val_eur*rate:,.2f} $)"

    def mostrar_seccion(titulo, filtro):
        st.header(f"💼 {titulo}")
        df_sub = df[df['Tipo'] == filtro].copy()
        
        # Resumen
        res = df_sub.groupby(['Nombre', 'Broker']).agg({'Cant':'sum','Coste':'sum','Valor_Actual':'sum','GP_EUR':'sum','P_Act':'first'}).reset_index()
        res['Rent. %'] = (res['GP_EUR'] / res['Coste'] * 100)
        
        # Aplicamos el formato de doble divisa a las columnas de interés
        res['Precio (EUR/USD)'] = res['P_Act'].apply(lambda x: f"{x:,.4f} € ({x*rate:,.2f} $)")
        res['Ganancia (EUR/USD)'] = res['GP_EUR'].apply(fmt_bimoneda)
        
        st.subheader(f"📊 Situación Actual ({titulo})")
        cols_mostrar = ['Broker', 'Nombre', 'Cant', 'Coste', 'Valor_Actual', 'Precio (EUR/USD)', 'Ganancia (EUR/USD)', 'Rent. %']
        
        st.dataframe(res[cols_mostrar].style.applymap(
            lambda x: f'background-color: {"#d4edda" if x > 0 else "#f8d7da"}' if isinstance(x, (int, float)) else None, 
            subset=['Ganancia (EUR/USD)', 'Rent. %'], # Nota: la lógica de color usa el valor real, pero Streamlit necesita mapeo cuidadoso
        ).format({"Cant":"{:.2f}","Coste":"{:.2f} €","Valor_Actual":"{:.2f} €","Rent. %":"{:.2f}%"}), use_container_width=True)

        # Historial
        st.subheader(f"📜 Detalle por Fechas ({titulo})")
        for n in df_sub['Nombre'].unique():
            h = df_sub[df_sub['Nombre'] == n].sort_values(by='Fecha', ascending=False).copy()
            h['Ganancia (EUR/USD)'] = h['GP_EUR'].apply(fmt_bimoneda)
            h['Precio'] = h['P_Act'].apply(lambda x: f"{x:,.4f} € ({x*rate:,.2f} $)")
            with st.expander(f"Ver historial: {n}"):
                st.table(h[['Fecha','Cant','Coste','Precio','Ganancia (EUR/USD)','Rent. %']].style.applymap(
                    lambda x: f'background-color: {"#d4edda" if x > 0 else "#f8d7da"}' if isinstance(x, (int, float)) else None, 
                    subset=['Ganancia (EUR/USD)', 'Rent. %']
                ).format({"Cant":"{:.4f}","Coste":"{:.2f} €","Rent. %":"{:.2f}%"}))

    mostrar_seccion("Acciones", "Acción")
    st.divider()
    mostrar_seccion("Fondos de Inversión", "Fondo")

    st.divider()
    st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución del Patrimonio", hole=0.4), use_container_width=True)
