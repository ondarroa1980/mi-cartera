import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date

# --- 0. CARGA SEGURA DE PDF ---
try:
    from fpdf import FPDF
    PDF_OK = True
except ImportError:
    PDF_OK = False

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
    
    # --- 3. FUNCIONES DE APOYO ---
    def resaltar(val):
        try:
            if isinstance(val, str): num = float(val.split(' ')[0].replace(',', ''))
            elif isinstance(val, (int, float)): num = val
            else: return None
            return 'background-color: #d4edda' if num > 0 else 'background-color: #f8d7da'
        except: return None

    def fmt_dual(v, mon, tasa):
        if mon == "USD": return f"{v:,.2f} € ({v * tasa:,.2f} $)"
        return f"{v:,.2f} €"

    # --- 4. BASES DE DATOS ---
    def cargar_datos_maestros():
        return [
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR"},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD"},
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR"}
        ]

    def cargar_diario_operaciones():
        return [
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "Compra", "Importe": 63822.16},
            {"Fecha": "2026-01-08", "Producto": "JPM US Short Duration", "Operación": "Venta", "Importe": -556.32}
        ]

    def cargar_aportaciones():
        return [
            {"Titular": "Ander", "Broker": "R4", "Fecha": date(2024, 8, 30), "Importe": 44000.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": date(2024, 8, 30), "Importe": 30000.0}
        ]

    # --- 5. PERSISTENCIA ---
    if 'df_cartera' not in st.session_state:
        st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
    if 'df_aportaciones' not in st.session_state:
        st.session_state.df_aportaciones = pd.DataFrame(cargar_aportaciones())

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
                st.success("Sincronizado")
            except: st.error("Sin conexión.")
            
        if PDF_OK:
            st.divider()
            st.download_button("📥 Descargar PDF", data=b"Resumen", file_name="Cartera.pdf")
        else:
            st.info("Nota: Sube requirements.txt para activar PDF")

    # --- 7. DASHBOARD ---
    st.title("🏦 Cartera Agirre & Uranga")
    rt = getattr(st.session_state, 'rate_aguirre', 1.09)
    df = st.session_state.df_cartera.copy()
    df['Val'] = df['P_Act'] * df['Cant']
    df['Ben'] = df['Val'] - df['Coste']

    c1, c2, c3 = st.columns(3)
    c1.metric("Invertido", f"{df['Coste'].sum():,.2f} €")
    c2.metric("Valor Actual", f"{df['Val'].sum():,.2f} €")
    c3.metric("Beneficio", f"{df['Ben'].sum():,.2f} €")
    st.divider()

    # --- 8. TABLAS ---
    def mostrar(tit, f):
        st.header(f"💼 {tit}")
        sub = df[df['Tipo'] == f].copy()
        res = sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Val':'sum','P_Act':'first','Ben':'sum'}).reset_index()
        res['Rent %'] = (res['Ben'] / res['Coste'] * 100)
        res['Beneficio (€/$)'] = res.apply(lambda x: fmt_dual(x['Ben'], x['Moneda'], rt), axis=1)
        
        st.dataframe(
            res.style.applymap(resaltar, subset=['Beneficio (€/$)'])
            .format({"Cant":"{:.4f}","Coste":"{:.2f} €","Val":"{:.2f} €","Rent %":"{:.2f}%"}),
            use_container_width=True
        )

    mostrar("Acciones", "Acción")
    mostrar("Fondos", "Fondo")

    # --- 9. DIARIO ---
    st.header("📜 Diario Histórico")
    st.dataframe(pd.DataFrame(cargar_diario_operaciones()).style.format({"Importe": "{:,.2f} €"}), use_container_width=True)

    # --- 10. APORTACIONES ---
    st.header("📑 Aportaciones Familiares")
    col_a, col_x = st.columns(2)
    # Corrección de tipo para evitar el error de la Imagen 3
    df_ap = st.session_state.df_aportaciones.copy()
    df_ap['Fecha'] = pd.to_datetime(df_ap['Fecha']).dt.date
    
    with col_a:
        st.subheader("Ander")
        ed_a = st.data_editor(df_ap[df_ap['Titular']=='Ander'][['Broker','Fecha','Importe']], key="ea", column_config={"Fecha": st.column_config.DateColumn()})
    with col_x:
        st.subheader("Xabat")
        ed_x = st.data_editor(df_ap[df_ap['Titular']=='Xabat'][['Broker','Fecha','Importe']], key="ex", column_config={"Fecha": st.column_config.DateColumn()})

    # --- 11. GRÁFICAS ---
    st.header("📊 Análisis Visual")
    st.plotly_chart(px.pie(df, values='Val', names='Nombre', title="Distribución Total"), use_container_width=True)
