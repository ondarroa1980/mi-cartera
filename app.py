import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date
from fpdf import FPDF

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Cartera Agirre & Uranga", layout="wide", page_icon="📈")

# --- 2. SEGURIDAD ---
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
    
    # --- 3. FUNCIONES ---
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

    def generar_resumen_pdf(inv, val, ben, t_a, t_x):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, "Resumen Cartera Agirre & Uranga", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Helvetica", '', 12)
        pdf.cell(0, 10, f"Invertido: {inv:,.2f} EUR", ln=True)
        pdf.cell(0, 10, f"Valor Actual: {val:,.2f} EUR", ln=True)
        pdf.cell(0, 10, f"Beneficio: {ben:,.2f} EUR", ln=True)
        pdf.ln(10)
        pdf.cell(0, 10, f"Ander: {t_a:,.2f} EUR | Xabat: {t_x:,.2f} EUR", ln=True)
        return pdf.output(dest='S').encode('latin-1', 'ignore')

    # --- 4. DATOS MAESTROS ---
    def cargar_datos_maestros():
        return [
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR"},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD"},
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"}
        ]

    def cargar_aportaciones():
        return [
            {"Titular": "Ander", "Broker": "R4", "Fecha": date(2024, 8, 30), "Importe": 44000.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": date(2024, 8, 30), "Importe": 30000.0}
        ]

    # --- 5. PERSISTENCIA ---
    ARCHIVO_CSV = "cartera_ Aguirre_Uranga.csv"
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

    # --- 7. DASHBOARD ---
    st.title("🏦 Cartera Agirre & Uranga")
    rt = getattr(st.session_state, 'rate_aguirre', 1.09)
    df = st.session_state.df_cartera.copy()
    df['Valor Actual'] = df['P_Act'] * df['Cant']
    df['Beneficio'] = df['Valor Actual'] - df['Coste']
    df['Rent %'] = (df['Beneficio'] / df['Coste'] * 100)

    m1, m2, m3 = st.columns(3)
    m1.metric("Dinero Invertido", f"{df['Coste'].sum():,.2f} €")
    m2.metric("Valor Cartera", f"{df['Valor Actual'].sum():,.2f} €")
    m3.metric("Beneficio TOTAL", f"{df['Beneficio'].sum():,.2f} €", f"{(df['Beneficio'].sum()/df['Coste'].sum()*100):.2f}%")

    # --- 8. TABLAS ---
    def mostrar(tit, f):
        st.header(f"💼 {tit}")
        sub = df[df['Tipo'] == f].copy()
        res = sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Valor Actual':'sum','P_Act':'first','Beneficio':'sum'}).reset_index()
        res['Rent %'] = (res['Beneficio'] / res['Coste'] * 100)
        res['Beneficio (€/$)'] = res.apply(lambda x: fmt_dual(x['Beneficio'], x['Moneda'], rt), axis=1)
        
        st.dataframe(
            res.style.applymap(resaltar_beneficio, subset=['Beneficio (€/$)'])
            .format({"Cant":"{:.4f}","Coste":"{:.2f} €","Valor Actual":"{:.2f} €","Rent %":"{:.2f}%"}),
            use_container_width=True
        )
    
    mostrar("Acciones", "Acción")
    mostrar("Fondos", "Fondo")

    # --- 9. APORTACIONES ---
    st.header("📑 Aportaciones Familiares")
    col_a, col_x = st.columns(2)
    with col_a:
        st.subheader("Ander")
        df_a = st.session_state.df_aportaciones[st.session_state.df_aportaciones['Titular'] == 'Ander'].copy()
        ed_a = st.data_editor(df_a[['Broker', 'Fecha', 'Importe']], num_rows="dynamic", key="ea", column_config={"Fecha": st.column_config.DateColumn()})
        t_a = ed_a['Importe'].sum()
    with col_x:
        st.subheader("Xabat")
        df_x = st.session_state.df_aportaciones[st.session_state.df_aportaciones['Titular'] == 'Xabat'].copy()
        ed_x = st.data_editor(df_x[['Broker', 'Fecha', 'Importe']], num_rows="dynamic", key="ex", column_config={"Fecha": st.column_config.DateColumn()})
        t_x = ed_x['Importe'].sum()

    # --- 10. PDF ---
    with st.sidebar:
        pdf_bytes = generar_resumen_pdf(df['Coste'].sum(), df['Valor Actual'].sum(), df['Beneficio'].sum(), t_a, t_x)
        st.download_button("📄 Descargar Resumen PDF", data=pdf_bytes, file_name="Cartera.pdf", mime="application/pdf")
