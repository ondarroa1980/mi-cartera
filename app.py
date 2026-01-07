import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Nuestra Cartera Familiar - Historial Real", layout="wide")

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
    
    # --- 3. BASE DE DATOS MAESTRA (Con ISINs del informe) ---
    def cargar_datos_maestros():
        return [
            # Datos extraídos del informe detallado
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 65.3287, "Coste": 10000.00, "P_Act": 160.22},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0562247428", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 310.156, "Coste": 7451.82, "P_Act": 25.93},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World", "Cant": 549.94, "Coste": 6516.20, "P_Act": 12.33},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 2870.0, "Coste": 2061.80, "P_Act": 0.718},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194}
        ]

    ARCHIVO_CSV = "cartera_v34.csv"
    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    # --- 4. SIDEBAR (Sincronización corregida) ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            with st.spinner("Actualizando precios..."):
                try:
                    # Tasa de cambio para activos en USD
                    rate_info = yf.Ticker("EURUSD=X").history(period="1d")
                    eurusd = rate_info["Close"].iloc[-1] if not rate_info.empty else 1.0
                    
                    for i, row in st.session_state.df_cartera.iterrows():
                        tk = yf.Ticker(row['Ticker'])
                        hist = tk.history(period="1d")
                        if not hist.empty:
                            p = hist["Close"].iloc[-1]
                            # Ajuste de divisa para acciones americanas
                            if row['Ticker'] in ['UNH', 'JD']:
                                p = p / eurusd
                            st.session_state.df_cartera.at[i, 'P_Act'] = p
                    
                    st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                    st.success("Cartera sincronizada")
                    st.rerun()
                except Exception as e:
                    st.warning(f"Sincronización parcial. Algunos datos no se pudieron recuperar.")

        if st.button("🚨 Reiniciar Datos"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.rerun()

    # --- 5. PROCESAMIENTO ---
    df = st.session_state.df_cartera.copy()
    df['Valor_Actual'] = df['P_Act'] * df['Cant']
    df['G/P (€)'] = df['Valor_Actual'] - df['Coste']
    df['Rent. %'] = (df['G/P (€)'] / df['Coste'] * 100).fillna(0)

    # --- 6. INTERFAZ PRINCIPAL ---
    st.title("🏦 Cuadro de Mando Patrimonial")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("G/P Acciones", f"{df[df['Tipo'] == 'Acción']['G/P (€)'].sum():,.2f} €")
    c2.metric("G/P Fondos", f"{df[df['Tipo'] == 'Fondo']['G/P (€)'].sum():,.2f} €")
    c3.metric("G/P TOTAL", f"{df['G/P (€)'].sum():,.2f} €")
    st.divider()

    def mostrar_seccion(titulo, filtro):
        st.header(f"💼 {titulo}")
        df_sub = df[df['Tipo'] == filtro]
        
        if filtro == "Fondo":
            st.warning("💡 **RELLENAR ESTO:** Haz doble clic en la casilla **'P_Act'** de la tabla resumen para actualizar el precio del banco.")
        
        resumen = df_sub.groupby(['Nombre', 'Broker']).agg({'Cant':'sum','Coste':'sum','Valor_Actual':'sum','G/P (€)':'sum', 'P_Act': 'first'}).reset_index()
        resumen['Rent. %'] = (resumen['G/P (€)'] / resumen['Coste'] * 100)
        
        st.subheader(f"📊 Situación Actual ({titulo})")
        st.dataframe(resumen[['Broker', 'Nombre', 'Cant', 'Coste', 'Valor_Actual', 'P_Act', 'G/P (€)', 'Rent. %']].style.applymap(lambda x: f'background-color: {"#d4edda" if x > 0 else "#f8d7da"}' if isinstance(x, (int, float)) else None, subset=['G/P (€)', 'Rent. %']).format({
            "Cant":"{:.2f}","Coste":"{:.2f} €","Valor_Actual":"{:.2f} €","P_Act":"{:.4f} €","G/P (€)":"{:.2f} €","Rent. %":"{:.2f}%"
        }), use_container_width=True)

    mostrar_seccion("Acciones", "Acción")
    mostrar_seccion("Fondos de Inversión", "Fondo")

    # --- 7. GRÁFICAS DE LÍNEAS CON HISTORIAL REAL ---
    st.divider()
    st.header("📈 Evolución Real de cada Activo")
    st.info("Estas gráficas muestran los altibajos reales del mercado descargando el historial diario.")

    # Generar gráficas reales
    for nombre in df['Nombre'].unique():
        asset = df[df['Nombre'] == nombre].iloc[0]
        ticker_id = asset['Ticker']
        fecha_compra = asset['Fecha']
        
        try:
            # Descargamos historial desde la fecha de compra
            hist_data = yf.download(ticker_id, start=fecha_compra, progress=False)
            if not hist_data.empty:
                hist_df = hist_data[['Close']].copy().reset_index()
                # Ajustar G/P: (Precio_Histórico * Cantidad) - Coste_Total
                hist_df['G/P (€)'] = (hist_df['Close'] * asset['Cant']) - asset['Coste']
                
                fig = px.line(hist_df, x='Date', y='G/P (€)', title=f"Historial: {nombre} ({ticker_id})")
                fig.update_traces(line_color='#28a745' if asset['G/P (€)'] >= 0 else '#dc3545')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write(f"⚠️ No hay historial disponible para {nombre} en Yahoo Finance. Se muestra línea base.")
                chart_base = pd.DataFrame([{'Date': fecha_compra, 'G/P (€)': 0}, {'Date': str(date.today()), 'G/P (€)': asset['G/P (€)']}])
                st.plotly_chart(px.line(chart_base, x='Date', y='G/P (€)', title=f"Rendimiento (Estimado): {nombre}"), use_container_width=True)
        except:
            st.error(f"Error al cargar historial para {nombre}")

    st.divider()
    st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución del Patrimonio", hole=0.4), use_container_width=True)
