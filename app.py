import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Nuestra Cartera Familiar - v34", layout="wide")

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
            # ACCIONES (MyInvestor)
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},

            # FONDOS RENTA 4 (Mapeados con Tickers de Yahoo para las gráficas)
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS6.DE", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI.HE", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI.HE", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "0P0001D486.F", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368},
            {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "0P0001D486.F", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.9368},
            {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "0P0001D486.F", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.9368},
            {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "0P0001D486.F", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.9368},
            {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "0P0001D486.F", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.9368},
            {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "0P0001D486.F", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.9368},

            # FONDOS MYINVESTOR
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IWDA.AS", "Nombre": "MSCI World Index", "Cant": 549.94, "Coste": 6516.20, "P_Act": 12.33},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51}
        ]

    ARCHIVO_CSV = "cartera_familiar_v34.csv"

    if 'df_cartera' not in st.session_state:
        try:
            st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    def resaltar_gp(val):
        color = '#d4edda' if val > 0 else '#f8d7da' if val < 0 else None
        return f'background-color: {color}'

    # --- 4. SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            try:
                rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                        st.session_state.df_cartera.at[i, 'P_Act'] = p / rate if row['Ticker'] in ['UNH', 'JD'] else p
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Error de red")
        
        st.divider()
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
            st.warning("💡 **RELLENAR ESTO:** Haz doble clic en la casilla 'P_Act' de la tabla resumen para actualizar el precio del banco.")
        
        res = df_sub.groupby(['Nombre', 'Broker']).agg({'Cant':'sum','Coste':'sum','Valor_Actual':'sum','G/P (€)':'sum'}).reset_index()
        res['Rent. %'] = (res['G/P (€)'] / res['Coste'] * 100)
        
        st.subheader(f"📊 Situación Actual ({titulo})")
        cols = ['Broker', 'Nombre', 'Cant', 'Coste', 'Valor_Actual', 'G/P (€)', 'Rent. %']
        st.dataframe(res[cols].style.applymap(resaltar_gp, subset=['G/P (€)', 'Rent. %']).format({
            "Cant":"{:.2f}","Coste":"{:.2f} €","Valor_Actual":"{:.2f} €","G/P (€)":"{:.2f} €","Rent. %":"{:.2f}%"
        }), use_container_width=True)
        
        st.subheader(f"📜 Historial de Operaciones ({titulo})")
        for n in df_sub['Nombre'].unique():
            h = df_sub[df_sub['Nombre'] == n].sort_values(by='Fecha', ascending=False)
            with st.expander(f"Detalle: {n}"):
                st.table(h[['Fecha','Cant','Coste','P_Act','G/P (€)','Rent. %']].style.applymap(resaltar_gp, subset=['G/P (€)', 'Rent. %']).format({
                    "Cant":"{:.4f}","Coste":"{:.2f} €","P_Act":"{:.4f} €","G/P (€)":"{:.2f} €","Rent. %":"{:.2f}%"
                }))

    mostrar_seccion("Acciones", "Acción")
    st.divider()
    mostrar_seccion("Fondos de Inversión", "Fondo")

    # --- 7. GRÁFICAS DE EVOLUCIÓN (ALTIBAJOS REALES) ---
    st.divider()
    st.header("📈 Evolución Histórica de Beneficios (€)")
    st.info("Estas gráficas muestran los altibajos reales del mercado desde la fecha de tu primera compra.")

    # Agrupamos por nombre para tener una gráfica por producto contratado
    nombres_productos = df['Nombre'].unique()
    
    # Crear columnas para las gráficas (2 por fila para que se vea bien en iPhone/PC)
    cols_graficas = st.columns(2)
    
    for i, nombre in enumerate(nombres_productos):
        with cols_graficas[i % 2]:
            # Datos del producto
            prod_info = df[df['Nombre'] == nombre]
            ticker = prod_info['Ticker'].iloc[0]
            fecha_inicio = prod_info['Fecha'].min()
            cant_total = prod_info['Cant'].sum()
            coste_total = prod_info['Coste'].sum()
            
            try:
                # Descargar historial real de Yahoo Finance
                historial = yf.download(ticker, start=fecha_inicio, interval="1d", progress=False)
                
                if not historial.empty:
                    # Calcular G/P diario: (Precio Cierre * Cantidad Total) - Coste Total
                    # Nota: simplificamos usando la cantidad total actual para todo el periodo
                    historial['G/P (€)'] = (historial['Close'] * cant_total) - coste_total
                    
                    fig = px.line(historial.reset_index(), x='Date', y='G/P (€)', 
                                  title=f"Rendimiento: {nombre}",
                                  labels={'Date': 'Fecha', 'G/P (€)': 'Ganancia/Pérdida (€)'})
                    
                    # Color de la línea: Verde si hoy gana, Rojo si pierde
                    color_linea = "#28a745" if historial['G/P (€)'].iloc[-1] >= 0 else "#dc3545"
                    fig.update_traces(line_color=color_linea)
                    
                    # Línea de equilibrio (cero)
                    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write(f"⚠️ No hay datos históricos suficientes para {nombre}")
            except:
                st.write(f"❌ Error al cargar datos para {nombre}")

    # Gráfico de tarta final
    st.divider()
    st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución del Patrimonio", hole=0.4), use_container_width=True)
