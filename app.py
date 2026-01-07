import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nuestra Cartera Familiar - v36", layout="wide")

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
        st.text_input("Introduce la contraseña familiar:", type="password", on_change=password_entered, key="password")
        return False
    return True

if check_password():
    
    # --- 3. BASE DE DATOS MAESTRA (RESTURADA DEL INFORME DETALLADO) ---
    def cargar_datos_maestros():
        return [
            # FONDOS RENTA 4
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS6.DE", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI.HE", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI.HE", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "0P0001D486.F", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.93},
            {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "0P0001D486.F", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.93},
            {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "0P0001D486.F", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.93},
            {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "0P0001D486.F", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.93},
            {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "0P0001D486.F", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.93},
            # FONDOS MYINVESTOR
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World", "Cant": 415.065, "Coste": 5000.00, "P_Act": 12.33},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World", "Cant": 1.33, "Coste": 16.20, "P_Act": 12.33},
            {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World", "Cant": 43.484, "Coste": 500.00, "P_Act": 12.33},
            {"Fecha": "2025-05-01", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World", "Cant": 47.216, "Coste": 500.00, "P_Act": 12.33},
            {"Fecha": "2025-08-13", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World", "Cant": 42.847, "Coste": 500.00, "P_Act": 12.33},
            # ACCIONES MYINVESTOR
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194}
        ]

    ARCHIVO_CSV = "cartera_final_v36.csv"
    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    # --- 4. SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            with st.spinner("Actualizando precios..."):
                try:
                    for i, row in st.session_state.df_cartera.iterrows():
                        stock = yf.Ticker(row['Ticker'])
                        hist = stock.history(period="1d")
                        if not hist.empty:
                            st.session_state.df_cartera.at[i, 'P_Act'] = hist["Close"].iloc[-1]
                    st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                    st.success("Precios actualizados")
                    st.rerun()
                except: st.warning("Aviso: Algunos datos de bolsa no están disponibles ahora.")
        
        if st.button("🚨 Reiniciar Datos"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.rerun()

    # --- 5. PROCESAMIENTO ---
    df = st.session_state.df_cartera.copy()
    df['Valor_Actual'] = df['P_Act'] * df['Cant']
    df['G/P (€)'] = df['Valor_Actual'] - df['Coste']
    df['Rent. %'] = (df['G/P (€)'] / df['Coste'] * 100).fillna(0)

    # --- 6. INTERFAZ ---
    st.title("🏦 Panel de Control Patrimonial")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("G/P Acciones", f"{df[df['Tipo'] == 'Acción']['G/P (€)'].sum():,.2f} €")
    col2.metric("G/P Fondos", f"{df[df['Tipo'] == 'Fondo']['G/P (€)'].sum():,.2f} €")
    col3.metric("G/P TOTAL", f"{df['G/P (€)'].sum():,.2f} €")
    st.divider()

    def mostrar_seccion(titulo, filtro):
        st.header(f"💼 {titulo}")
        df_sub = df[df['Tipo'] == filtro]
        
        if filtro == "Fondo":
            st.warning("💡 **RELLENAR ESTO:** Haz doble clic en la casilla **'P_Act'** de la tabla resumen para actualizar el precio del banco.")
        
        # Resumen Agrupado
        res = df_sub.groupby(['Nombre', 'Broker']).agg({'Cant':'sum','Coste':'sum','Valor_Actual':'sum','G/P (€)':'sum','P_Act':'first'}).reset_index()
        res['Rent. %'] = (res['G/P (€)'] / res['Coste'] * 100)
        
        st.subheader(f"📊 Situación Actual ({titulo})")
        st.dataframe(res[['Broker','Nombre','Cant','Coste','Valor_Actual','P_Act','G/P (€)','Rent. %']].style.applymap(
            lambda x: f'background-color: {"#d4edda" if x > 0 else "#f8d7da"}' if isinstance(x, (int, float)) else None, 
            subset=['G/P (€)', 'Rent. %']).format({
            "Cant":"{:.2f}","Coste":"{:.2f} €","Valor_Actual":"{:.2f} €","P_Act":"{:.4f} €","G/P (€)":"{:.2f} €","Rent. %":"{:.2f}%"
        }), use_container_width=True)
        
        # HISTORIAL DESGLOSADO (Recuperado)
        st.subheader(f"📜 Detalle por Compras ({titulo})")
        for n in df_sub['Nombre'].unique():
            h = df_sub[df_sub['Nombre'] == n].sort_values(by='Fecha', ascending=False)
            with st.expander(f"Ver historial de compras: {n}"):
                st.table(h[['Fecha','Cant','Coste','P_Act','G/P (€)','Rent. %']].style.applymap(
                    lambda x: f'background-color: {"#d4edda" if x > 0 else "#f8d7da"}' if isinstance(x, (int, float)) else None, 
                    subset=['G/P (€)', 'Rent. %']).format({
                    "Cant":"{:.4f}","Coste":"{:.2f} €","P_Act":"{:.4f} €","G/P (€)":"{:.2f} €","Rent. %":"{:.2f}%"
                }))

    mostrar_seccion("Acciones", "Acción")
    st.divider()
    mostrar_seccion("Fondos de Inversión", "Fondo")

    # --- 7. GRÁFICAS DE LÍNEAS (CON ALTIBAJOS) ---
    st.divider()
    st.header("📈 Evolución de Ganancias por Producto")
    st.info("Gráficas históricas que muestran la volatilidad real del mercado.")

    for nombre in df['Nombre'].unique():
        asset = df[df['Nombre'] == nombre].iloc[0]
        try:
            h_data = yf.download(asset['Ticker'], start=asset['Fecha'], progress=False)
            if not h_data.empty:
                h_df = h_data[['Close']].copy().reset_index()
                h_df['Beneficio (€)'] = (h_df['Close'] * asset['Cant']) - asset['Coste']
                fig = px.line(h_df, x='Date', y='Beneficio (€)', title=f"Historial: {nombre}")
                fig.update_traces(line_color='#28a745' if asset['G/P (€)'] >= 0 else '#dc3545')
                st.plotly_chart(fig, use_container_width=True)
        except: continue

    st.divider()
    st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución de la Cartera", hole=0.4), use_container_width=True)
