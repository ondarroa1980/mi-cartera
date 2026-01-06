import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser la primera instrucción)
st.set_page_config(page_title="Gestor Patrimonial Consolidado", layout="wide")

# 2. SISTEMA DE SEGURIDAD
def check_password():
    def password_entered():
        if st.session_state["password"] == "1234": # <--- CONTRASEÑA POR DEFECTO
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 Acceso Privado")
        st.text_input("Introduce la clave familiar para acceder:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 Acceso Privado")
        st.text_input("Contraseña incorrecta:", type="password", on_change=password_entered, key="password")
        st.error("😕 Clave errónea. Inténtalo de nuevo.")
        return False
    return True

if check_password():
    
    # --- BASE DE DATOS MAESTRA (Fusión de todos tus documentos) ---
    def cargar_datos_maestros():
        return [
            # --- ACCIONES MYINVESTOR ---
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "ID": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "ID": "ES0126962069", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "ID": "ES0126962069", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "ID": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "ID": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},

            # --- FONDOS RENTA 4 (Datos del informe de plusvalías) ---
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "ID": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "ID": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "ID": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "ID": "LU0562247428", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "ID": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.93},
            {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "ID": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.93},
            {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "ID": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.93},
            {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "ID": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.93},
            {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "ID": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.93},
            {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "ID": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.93},

            # --- FONDOS MYINVESTOR (Desglose individual) ---
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "ID": "IE00BYX5NX33", "Nombre": "MSCI World", "Cant": 415.065, "Coste": 5000.00, "P_Act": 12.33},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "ID": "IE00BYX5NX33", "Nombre": "MSCI World", "Cant": 1.33, "Coste": 16.20, "P_Act": 12.33},
            {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "MyInvestor", "ID": "IE00BYX5NX33", "Nombre": "MSCI World", "Cant": 43.484, "Coste": 500.00, "P_Act": 12.33},
            {"Fecha": "2025-05-01", "Tipo": "Fondo", "Broker": "MyInvestor", "ID": "IE00BYX5NX33", "Nombre": "MSCI World", "Cant": 47.216, "Coste": 500.00, "P_Act": 12.33},
            {"Fecha": "2025-08-13", "Tipo": "Fondo", "Broker": "MyInvestor", "ID": "IE00BYX5NX33", "Nombre": "MSCI World", "Cant": 42.847, "Coste": 500.00, "P_Act": 12.33},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "ID": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51}
        ]

    # Gestión de persistencia de datos
    ARCHIVO_CSV = "cartera_completa_v30.csv"
    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    # Lógica de colores (Verde: Ganancia / Rojo: Pérdida)
    def estilo_gp(val):
        color = '#d4edda' if val > 0 else '#f8d7da' if val < 0 else None
        return f'background-color: {color}'

    # Cálculos dinámicos
    df = st.session_state.df_cartera.copy()
    df['Valor_Actual'] = df['P_Act'] * df['Cant']
    df['Ganancia (€)'] = df['Valor_Actual'] - df['Coste']
    df['Rent. %'] = (df['Ganancia (€)'] / df['Coste'] * 100).fillna(0)

    # --- INTERFAZ ---
    st.title("🏦 Nuestra Cartera Familiar Consolidada")
    
    # Métricas Globales
    m1, m2, m3 = st.columns(3)
    b_acc = df[df['Tipo'] == "Acción"]['Ganancia (€)'].sum()
    b_fon = df[df['Tipo'] == "Fondo"]['Ganancia (€)'].sum()
    m1.metric("Beneficio Acciones", f"{b_acc:,.2f} €")
    m2.metric("Beneficio Fondos", f"{b_fon:,.2f} €")
    m3.metric("BENEFICIO TOTAL", f"{(b_acc + b_fon):,.2f} €")
    st.divider()

    # Función para dibujar tablas con colores y orden
    def dibujar_seccion(titulo, filtro):
        st.header(f"💼 {titulo}")
        df_sub = df[df['Tipo'] == filtro]
        
        # 📊 TABLA RESUMEN
        res = df_sub.groupby(['Nombre', 'ID', 'Broker']).agg({
            'Cant': 'sum', 'Coste': 'sum', 'Valor_Actual': 'sum', 'Ganancia (€)': 'sum'
        }).reset_index()
        res['Rent. %'] = (res['Ganancia (€)'] / res['Coste'] * 100)
        
        st.subheader(f"📊 Resumen de Posiciones")
        # Forzamos que ID (ISIN) esté visible y las ganancias al final
        cols_res = ['Broker', 'Nombre', 'ID', 'Cant', 'Coste', 'Valor_Actual', 'Ganancia (€)', 'Rent. %']
        st.dataframe(res[cols_res].style.applymap(estilo_gp, subset=['Ganancia (€)', 'Rent. %']).format({
            "Cant": "{:.2f}", "Coste": "{:.2f} €", "Valor_Actual": "{:.2f} €", "Ganancia (€)": "{:.2f} €", "Rent. %": "{:.2f}%"
        }), use_container_width=True)
        
        # 🔍 TABLA DETALLE (DESPLEGABLE)
        st.subheader(f"📜 Detalle Histórico de Compras")
        for n in df_sub['Nombre'].unique():
            h = df_sub[df_sub['Nombre'] == n].sort_values(by='Fecha', ascending=False)
            with st.expander(f"Ver todas las compras de: {n}"):
                cols_hist = ['Fecha', 'Cant', 'Coste', 'P_Act', 'Ganancia (€)', 'Rent. %']
                st.table(h[cols_hist].style.applymap(estilo_gp, subset=['Ganancia (€)', 'Rent. %']).format({
                    "Cant": "{:.4f}", "Coste": "{:.2f} €", "P_Act": "{:.4f} €", "Ganancia (€)": "{:.2f} €", "Rent. %": "{:.2f}%"
                }))

    dibujar_seccion("Acciones", "Acción")
    st.divider()
    dibujar_seccion("Fondos de Inversión", "Fondo")

    # --- SIDEBAR (HERRAMIENTAS) ---
    with st.sidebar:
        st.header("⚙️ Herramientas")
        if st.button("🔄 Actualizar Bolsa Ahora"):
            try:
                rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        ticker = row['ID'] if row['ID'] != "ES0126962069" else "NXT.MC"
                        p = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
                        st.session_state.df_cartera.at[i, 'P_Act'] = p / rate if ticker in ['UNH', 'JD'] else p
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Error al conectar con Yahoo Finance.")
        
        st.divider()
        st.header("➕ Añadir Activo")
        with st.form("nuevo"):
            t = st.selectbox("Tipo", ["Acción", "Fondo"])
            b = st.selectbox("Broker", ["MyInvestor", "Renta 4"])
            f = st.date_input("Fecha")
            nom = st.text_input("Nombre")
            id_in = st.text_input("Ticker / ISIN").upper()
            c = st.number_input("Cantidad", min_value=0.0)
            cos = st.number_input("Coste Total (€)", min_value=0.0)
            pa = st.number_input("Precio Actual (€)", min_value=0.0)
            if st.form_submit_button("Guardar en Cartera"):
                nuevo = pd.DataFrame([{"Fecha": str(f), "Tipo": t, "Broker": b, "ID": id_in, "Nombre": nom, "Cant": c, "Coste": cos, "P_Act": pa}])
                st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, nuevo], ignore_index=True)
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()

        if st.button("🚨 Resetear a Datos de Fábrica"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.rerun()
