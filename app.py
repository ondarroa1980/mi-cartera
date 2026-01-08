import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date

# --- 0. CARGA SEGURA DE PDF ---
try:
    from fpdf import FPDF
    PDF_DISPONIBLE = True
except ImportError:
    PDF_DISPONIBLE = False

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cartera Agirre & Uranga", layout="wide", page_icon="📈")

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
    return True

if check_password():
    
    # --- 3. FUNCIONES DE APOYO ---
    def resaltar_beneficio(val):
        try:
            if isinstance(val, str):
                num = float(val.split(' ')[0].replace(',', ''))
            elif isinstance(val, (int, float)):
                num = val
            else: return None
            if num > 0: return 'background-color: #d4edda'
            if num < 0: return 'background-color: #f8d7da'
        except: pass
        return None

    def fmt_dual(valor_eur, moneda, tasa, decimales=2):
        if moneda == "USD":
            return f"{valor_eur:,.{decimales}f} € ({valor_eur * tasa:,.2f} $)"
        return f"{valor_eur:,.{decimales}f} €"

    # --- 4. BASE DE DATOS COMPLETA (RECUPERADA) ---
    def cargar_datos_maestros():
        return [
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR"},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR"},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Moneda": "EUR"},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD"},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50, "Moneda": "USD"},
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Moneda": "EUR"},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22, "Moneda": "EUR"},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR"}
        ]

    def cargar_diario():
        return [
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "Compra", "Importe": 63822.16},
            {"Fecha": "2026-01-08", "Producto": "JPM US Short Duration", "Operación": "VENTA", "Importe": -556.32}
        ]

    def cargar_aportaciones():
        return [
            {"Titular": "Ander", "Broker": "R4", "Fecha": date(2024, 8, 30), "Importe": 44000.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": date(2024, 8, 30), "Importe": 30000.0}
        ]

    # --- 5. GESTIÓN DE ARCHIVOS ---
    ARCHIVO_CSV = "cartera_final_aguirre_uranga.csv"
    ARCHIVO_AP = "aportaciones_familiares.csv"

    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except: st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())

    if 'df_aportaciones' not in st.session_state:
        try: 
            df_temp = pd.read_csv(ARCHIVO_AP)
            df_temp['Fecha'] = pd.to_datetime(df_temp['Fecha']).dt.date
            st.session_state.df_aportaciones = df_temp
        except: 
            df_temp = pd.DataFrame(cargar_aportaciones())
            st.session_state.df_aportaciones = df_temp

    # --- 6. BARRA LATERAL ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            try:
                rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
                st.session_state.rate_aguirre = rate
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                        st.session_state.df_cartera.at[i, 'P_Act'] = p / rate if row['Moneda'] == "USD" else p
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Sin conexión.")

        if PDF_DISPONIBLE:
            st.divider()
            st.header("🖨️ Informes")
            # Lógica simple de PDF para evitar errores de encoding
            if st.button("Generar Informe"):
                st.success("PDF listo para descargar (Añade download_button)")
        else:
            st.warning("⚠️ Instala 'fpdf' en GitHub para activar informes.")

    # --- 7. DASHBOARD ---
    st.title("🏦 Cartera Agirre & Uranga")
    rt = getattr(st.session_state, 'rate_aguirre', 1.09)
    df = st.session_state.df_cartera.copy()
    df['Valor Actual'] = df['P_Act'] * df['Cant']
    df['Beneficio'] = df['Valor Actual'] - df['Coste']
    df['Rent %'] = (df['Beneficio'] / df['Coste'] * 100)

    c1, c2, c3 = st.columns(3)
    c1.metric("Invertido", f"{df['Coste'].sum():,.2f} €")
    c2.metric("Valor", f"{df['Valor Actual'].sum():,.2f} €")
    c3.metric("Beneficio", f"{df['Beneficio'].sum():,.2f} €", f"{(df['Beneficio'].sum()/df['Coste'].sum()*100):.2f}%")

    # --- 8. TABLAS ---
    def mostrar(tit, f):
        st.header(f"💼 {tit}")
        sub = df[df['Tipo'] == f].copy()
        res = sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Valor Actual':'sum','P_Act':'first','Beneficio':'sum'}).reset_index()
        res['Rent %'] = (res['Beneficio'] / res['Coste'] * 100)
        res['Beneficio (€/$)'] = res.apply(lambda x: fmt_dual(x['Beneficio'], x['Moneda'], rt), axis=1)
        
        # FIX: Usar style.format para evitar AttributeError
        st.dataframe(
            res.style.applymap(resaltar_beneficio, subset=['Beneficio (€/$)'])
            .format({"Cant":"{:.4f}","Coste":"{:.2f} €","Valor Actual":"{:.2f} €","Rent %":"{:.2f}%"}),
            use_container_width=True
        )
    
    mostrar("Acciones", "Acción")
    mostrar("Fondos de Inversión", "Fondo")

    # --- 9. DIARIO ---
    st.header("📜 Diario Histórico")
    st.dataframe(pd.DataFrame(cargar_diario()), use_container_width=True)

    # --- 10. APORTACIONES ---
    st.header("📑 Aportaciones Familiares")
    col_a, col_x = st.columns(2)
    with col_a:
        st.subheader("👨‍💼 Ander")
        df_a = st.session_state.df_aportaciones[st.session_state.df_aportaciones['Titular'] == 'Ander'].copy()
        ed_a = st.data_editor(df_a[['Broker', 'Fecha', 'Importe']], num_rows="dynamic", key="ea", column_config={"Fecha": st.column_config.DateColumn()})
    with col_x:
        st.subheader("👨‍💼 Xabat")
        df_x = st.session_state.df_aportaciones[st.session_state.df_aportaciones['Titular'] == 'Xabat'].copy()
        ed_x = st.data_editor(df_x[['Broker', 'Fecha', 'Importe']], num_rows="dynamic", key="ex", column_config={"Fecha": st.column_config.DateColumn()})

    # --- 11. GRÁFICAS ---
    st.header("📊 Análisis Visual")
    st.plotly_chart(px.pie(df, values='Valor Actual', names='Nombre', title="Distribución Global"), use_container_width=True)
