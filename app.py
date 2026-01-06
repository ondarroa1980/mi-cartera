import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# --- CONFIGURACIÓN DE SEGURIDAD ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "1234": # <--- CAMBIA ESTA CONTRASEÑA AQUÍ
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 Acceso Privado")
        st.text_input("Introduce la contraseña para ver la cartera:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 Acceso Privado")
        st.text_input("Contraseña incorrecta. Inténtalo de nuevo:", type="password", on_change=password_entered, key="password")
        st.error("😕 Ups, esa no es.")
        return False
    else:
        return True

if check_password():
    # --- TODO TU CÓDIGO ACTUAL VA AQUÍ ABAJO ---
    st.set_page_config(page_title="Nuestra Cartera", layout="wide")
    
    # Datos cargados del informe detallado
    def cargar_datos():
        return [
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 65.3287, "Coste": 10000.00, "P_Act": 160.22},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 329.434, "Coste": 7951.82, "P_Act": 25.93},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0562247428", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.94, "Coste": 6516.20, "P_Act": 12.33},
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194}
        ]
    
    # Carga de archivos y resto de lógica que ya teníamos (Resumen, Historial y Colores)...
    # (Pega aquí el resto del código v25 que ya funciona)
    st.success("¡Bienvenido! Los datos están actualizados.")
