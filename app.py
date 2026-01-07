import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Inversiones Familiares - Gráficas Reales", layout="wide")

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
        st.text_input("Contraseña:", type="password", on_change=password_entered, key="password")
        return False
    return True

if check_password():
    # --- 3. DATOS MAESTROS (Con Tickers compatibles con Yahoo Finance) ---
    def cargar_datos():
        return [
            # Fondos (Usando equivalentes de Yahoo para tener gráficas con altibajos)
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS6.DE", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI.HE", "Nombre": "Evli Nordic Corp", "Cant": 65.3287, "Coste": 10000.00, "P_Act": 160.22},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "0P0001D486.F", "Nombre": "Numantia Patrimonio", "Cant": 310.156, "Coste": 7451.82, "P_Act": 25.93},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World", "Cant": 549.94, "Coste": 6516.20, "P_Act": 12.33},
            # Acciones
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 2870.0, "Coste": 2061.80, "P_Act": 0.718},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194}
        ]

    CSV_FILE = "cartera_v35.csv"
    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(CSV_FILE)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos())
            st.session_state.df_cartera.to_csv(CSV_FILE, index=False)

    # --- 4. BARRA LATERAL ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            with st.spinner("Conectando con mercados..."):
                try:
                    for i, row in st.session_state.df_cartera.iterrows():
                        stock = yf.Ticker(row['Ticker'])
                        hist = stock.history(period="1d")
                        if not hist.empty:
                            st.session_state.df_cartera.at[i, 'P_Act'] = hist["Close"].iloc[-1]
                    st.session_state.df_cartera.to_csv(CSV_FILE, index=False)
                    st.rerun()
                except: st.warning("Aviso: Algunos precios se actualizarán en el próximo intento.")

        if st.button("🚨 Reiniciar"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos())
            st.session_state.df_cartera.to_csv(CSV_FILE, index=False)
            st.rerun()

    # --- 5. PROCESAMIENTO ---
    df = st.session_state.df_cartera.copy()
    df['Valor_Actual'] = df['P_Act'] * df['Cant']
    df['G/P (€)'] = df['Valor_Actual'] - df['Coste']

    # --- 6. INTERFAZ ---
    st.title("🏦 Cuadro de Mando Patrimonial")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("G/P Acciones", f"{df[df['Tipo'] == 'Acción']['G/P (€)'].sum():,.2f} €")
    col2.metric("G/P Fondos", f"{df[df['Tipo'] == 'Fondo']['G/P (€)'].sum():,.2f} €")
    col3.metric("G/P TOTAL GLOBAL", f"{df['G/P (€)'].sum():,.2f} €")
    st.divider()

    def mostrar_bloque(titulo, filtro):
        st.header(f"💼 {titulo}")
        df_sub = df[df['Tipo'] == filtro]
        
        if filtro == "Fondo":
            st.warning("💡 **RELLENAR ESTO:** Doble clic en 'P_Act' de la tabla para actualizar el precio del banco.")
        
        res = df_sub.groupby(['Nombre', 'Broker']).agg({'Cant':'sum','Coste':'sum','Valor_Actual':'sum','G/P (€)':'sum','P_Act':'first'}).reset_index()
        res['Rent. %'] = (res['G/P (€)'] / res['Coste'] * 100)
        
        # Tabla Principal
        st.dataframe(res[['Broker', 'Nombre', 'Cant', 'Coste', 'Valor_Actual', 'P_Act', 'G/P (€)', 'Rent. %']].style.applymap(
            lambda x: f'background-color: {"#d4edda" if x > 0 else "#f8d7da"}' if isinstance(x, (int, float)) else None, 
            subset=['G/P (€)', 'Rent. %']).format({
            "Cant":"{:.2f}","Coste":"{:.2f} €","Valor_Actual":"{:.2f} €","P_Act":"{:.4f} €","G/P (€)":"{:.2f} €","Rent. %":"{:.2f}%"
        }), use_container_width=True)

    mostrar_bloque("Acciones", "Acción")
    mostrar_bloque("Fondos de Inversión", "Fondo")

    # --- 7. GRÁFICAS DE LÍNEAS (ALTIBAJOS REALES) ---
    st.divider()
    st.header("📈 Evolución de Ganancias por Producto")
    st.info("Estas gráficas descargan el historial diario para mostrar la volatilidad real.")

    for nombre in df['Nombre'].unique():
        asset = df[df['Nombre'] == nombre].iloc[0]
        with st.container():
            try:
                # Descargamos historial real
                h_data = yf.download(asset['Ticker'], start=asset['Fecha'], progress=False)
                if not h_data.empty:
                    h_df = h_data[['Close']].copy().reset_index()
                    h_df['Beneficio (€)'] = (h_df['Close'] * asset['Cant']) - asset['Coste']
                    
                    fig = px.line(h_df, x='Date', y='Beneficio (€)', title=f"Rendimiento Histórico: {nombre}")
                    fig.update_traces(line_color='#28a745' if asset['G/P (€)'] >= 0 else '#dc3545')
                    fig.add_hline(y=0, line_dash="dash", line_color="gray")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write(f"📉 {nombre}: Gráfica en espera de más datos históricos.")
            except:
                st.write(f"⚠️ No se pudo cargar la gráfica para {nombre}.")

    st.divider()
    st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución del Patrimonio", hole=0.4), use_container_width=True)
