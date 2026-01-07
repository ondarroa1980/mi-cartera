import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Nuestra Cartera Familiar", layout="wide")

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
    
    # --- 3. BASE DE DATOS MAESTRA (ACTUALIZADA CON TUS DATOS REALES) ---
    def cargar_datos_maestros():
        return [
            # ACCIONES (MyInvestor)
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR"},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR"},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Moneda": "EUR"},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD"},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50, "Moneda": "USD"},

            # FONDOS RENTA 4
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Moneda": "EUR"},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22, "Moneda": "EUR"},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0562247428", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02, "Moneda": "EUR"},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},

            # FONDOS MYINVESTOR (Actualizado con tu imagen: Participaciones 549.94 y Invertido 6516.20)
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR"}
        ]

    # Gestión de archivos
    ARCHIVO_CSV = "cartera_familiar_v35.csv"
    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    # Lógica de colores
    def resaltar_gp(val):
        color = '#d4edda' if val > 0 else '#f8d7da' if val < 0 else None
        return f'background-color: {color}'

    # --- 4. BARRA LATERAL (Sincronización con Divisa) ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            try:
                # Obtener tipo de cambio EUR/USD
                rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
                st.session_state.cambio_usd = rate
                
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        p_raw = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                        if row['Moneda'] == "USD":
                            # Guardamos el precio en Euros, pero sabemos que viene de USD
                            st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate
                        else:
                            st.session_state.df_cartera.at[i, 'P_Act'] = p_raw
                
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Error al sincronizar con Yahoo Finance.")
        
        if st.button("🚨 Reiniciar Datos"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.rerun()

    # --- 5. PROCESAMIENTO ---
    df = st.session_state.df_cartera.copy()
    rate_usd = getattr(st.session_state, 'cambio_usd', 1.09) # Valor por defecto si no hay sync
    
    df['Valor_Actual'] = df['P_Act'] * df['Cant']
    df['G/P (€)'] = df['Valor_Actual'] - df['Coste']
    df['Rent. %'] = (df['G/P (€)'] / df['Coste'] * 100).fillna(0)

    # --- 6. INTERFAZ ---
    st.title("🏦 Cuadro de Mando Patrimonial")

    # Métricas principales
    c1, c2, c3 = st.columns(3)
    c1.metric("G/P Acciones", f"{df[df['Tipo'] == 'Acción']['G/P (€)'].sum():,.2f} €")
    c2.metric("G/P Fondos", f"{df[df['Tipo'] == 'Fondo']['G/P (€)'].sum():,.2f} €")
    c3.metric("G/P TOTAL GLOBAL", f"{df['G/P (€)'].sum():,.2f} €")
    st.divider()

    def mostrar_seccion(titulo, filtro):
        st.header(f"💼 {titulo}")
        df_sub = df[df['Tipo'] == filtro].copy()
        
        if filtro == "Fondo":
            st.warning("💡 **RELLENAR ESTO:** Haz doble clic en la casilla 'P_Act' de la tabla resumen para actualizar el precio del banco.")
        
        # Agrupación para el resumen
        res = df_sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Valor_Actual':'sum','G/P (€)':'sum', 'P_Act': 'first'}).reset_index()
        res['Rent. %'] = (res['G/P (€)'] / res['Coste'] * 100)
        
        # --- FORMATEO DINÁMICO DE DIVISA ---
        def formatear_precio(row):
            if row['Moneda'] == "USD":
                precio_usd = row['P_Act'] * rate_usd
                return f"{row['P_Act']:.2f} € ({precio_usd:.2f} $)"
            return f"{row['P_Act']:.4f} €"

        res['Precio'] = res.apply(formatear_precio, axis=1)
        
        st.subheader(f"📊 Situación Actual ({titulo})")
        cols = ['Broker', 'Nombre', 'Cant', 'Coste', 'Valor_Actual', 'Precio', 'G/P (€)', 'Rent. %']
        
        st.dataframe(res[cols].style.applymap(resaltar_gp, subset=['G/P (€)', 'Rent. %']).format({
            "Cant":"{:.2f}","Coste":"{:.2f} €","Valor_Actual":"{:.2f} €","G/P (€)":"{:.2f} €","Rent. %":"{:.2f}%"
        }), use_container_width=True)
        
        # HISTORIAL
        st.subheader(f"📜 Historial de Operaciones ({titulo})")
        for n in df_sub['Nombre'].unique():
            h = df_sub[df_sub['Nombre'] == n].sort_values(by='Fecha', ascending=False).copy()
            h['Precio'] = h.apply(formatear_precio, axis=1)
            with st.expander(f"Detalle: {n}"):
                st.table(h[['Fecha','Cant','Coste','Precio','G/P (€)','Rent. %']].style.applymap(resaltar_gp, subset=['G/P (€)', 'Rent. %']).format({
                    "Cant":"{:.4f}","Coste":"{:.2f} €","G/P (€)":"{:.2f} €","Rent. %":"{:.2f}%"
                }))

    mostrar_seccion("Acciones", "Acción")
    st.divider()
    mostrar_seccion("Fondos de Inversión", "Fondo")

    # Gráfico circular
    st.divider()
    st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución del Patrimonio", hole=0.4), use_container_width=True)
