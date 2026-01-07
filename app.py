import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Nuestra Cartera Familiar - Historial", layout="wide")

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
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50},
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0562247428", "Nombre": "JPM US Short Duration", "Cant": 87.425, "Coste": 9999.96, "P_Act": 108.02},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 329.434, "Coste": 7951.82, "P_Act": 25.9368},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.94, "Coste": 6516.20, "P_Act": 12.33},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51}
        ]

    ARCHIVO_CSV = "cartera_familiar_v33.csv"
    HISTORIAL_CSV = "historial_precios_v33.csv"

    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    # Inicializar historial si no existe
    if 'df_historial' not in st.session_state:
        try: st.session_state.df_historial = pd.read_csv(HISTORIAL_CSV)
        except:
            st.session_state.df_historial = pd.DataFrame(columns=['Fecha', 'Nombre', 'G_P'])

    def registrar_punto_historial(df_actual):
        hoy = str(date.today())
        puntos = []
        for nombre in df_actual['Nombre'].unique():
            sub = df_actual[df_actual['Nombre'] == nombre]
            valor_t = (sub['P_Act'] * sub['Cant']).sum()
            coste_t = sub['Coste'].sum()
            puntos.append({'Fecha': hoy, 'Nombre': nombre, 'G_P': valor_t - coste_t})
        
        nuevo_hist = pd.concat([st.session_state.df_historial, pd.DataFrame(puntos)], ignore_index=True).drop_duplicates(subset=['Fecha', 'Nombre'], keep='last')
        st.session_state.df_historial = nuevo_hist
        st.session_state.df_historial.to_csv(HISTORIAL_CSV, index=False)

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
                        ticker = yf.Ticker(row['Ticker'])
                        hist = ticker.history(period="1d")
                        if not hist.empty:
                            p = hist["Close"].iloc[-1]
                            st.session_state.df_cartera.at[i, 'P_Act'] = p / rate if row['Ticker'] in ['UNH', 'JD'] else p
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                registrar_punto_historial(st.session_state.df_cartera)
                st.rerun()
            except: st.error("Error de conexión")
        
        if st.button("🚨 Reiniciar Datos"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.session_state.df_historial = pd.DataFrame(columns=['Fecha', 'Nombre', 'G_P'])
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
            st.warning("💡 **RELLENAR ESTO:** Haz doble clic en la casilla **'P_Act'** de la tabla resumen para actualizar el precio del banco.")
        
        resumen = df_sub.groupby(['Nombre', 'Broker']).agg({'Cant':'sum','Coste':'sum','Valor_Actual':'sum','G/P (€)':'sum', 'P_Act': 'first'}).reset_index()
        resumen['Rent. %'] = (resumen['G/P (€)'] / resumen['Coste'] * 100)
        
        st.subheader(f"📊 Situación Actual ({titulo})")
        # Permitir edición de P_Act en el resumen para fondos
        if filtro == "Fondo":
            edited = st.data_editor(resumen[['Broker', 'Nombre', 'Cant', 'Coste', 'Valor_Actual', 'P_Act', 'G/P (€)', 'Rent. %']].style.applymap(resaltar_gp, subset=['G/P (€)', 'Rent. %']).format({
                "Cant":"{:.2f}","Coste":"{:.2f} €","Valor_Actual":"{:.2f} €","P_Act":"{:.4f} €","G/P (€)":"{:.2f} €","Rent. %":"{:.2f}%"
            }), use_container_width=True, key=f"editor_{filtro}")
            
            # Guardar cambios manuales
            for i, row in edited.iterrows():
                st.session_state.df_cartera.loc[st.session_state.df_cartera['Nombre'] == row['Nombre'], 'P_Act'] = row['P_Act']
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            registrar_punto_historial(st.session_state.df_cartera)
        else:
            st.dataframe(resumen[['Broker', 'Nombre', 'Cant', 'Coste', 'Valor_Actual', 'P_Act', 'G/P (€)', 'Rent. %']].style.applymap(resaltar_gp, subset=['G/P (€)', 'Rent. %']).format({
                "Cant":"{:.2f}","Coste":"{:.2f} €","Valor_Actual":"{:.2f} €","P_Act":"{:.4f} €","G/P (€)":"{:.2f} €","Rent. %":"{:.2f}%"
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

    # --- 7. GRÁFICAS DE LÍNEAS (Rendimiento desde contratación) ---
    st.divider()
    st.header("📈 Evolución de Ganancias por Producto")
    st.info("Estas gráficas reflejan el beneficio acumulado (€) desde la fecha de compra.")
    
    # Generar gráficas para cada producto
    cols_graf = st.columns(2)
    for idx, nombre in enumerate(df['Nombre'].unique()):
        sub_hist = st.session_state.df_historial[st.session_state.df_historial['Nombre'] == nombre]
        
        # Si no hay historial, crear punto inicial (Compra) y final (Hoy)
        asset_data = df[df['Nombre'] == nombre]
        fecha_inicio = asset_data['Fecha'].min()
        gp_actual = asset_data['G/P (€)'].sum()
        
        chart_data = pd.DataFrame([
            {'Fecha': fecha_inicio, 'G/P (€)': 0}, # Al inicio la ganancia es 0
            {'Fecha': str(date.today()), 'G/P (€)': gp_actual}
        ])
        
        # Combinar con historial guardado si existe
        if not sub_hist.empty:
            sub_hist = sub_hist.rename(columns={'G_P': 'G/P (€)'})
            chart_data = pd.concat([chart_data, sub_hist]).drop_duplicates(subset=['Fecha']).sort_values('Fecha')

        fig = px.line(chart_data, x='Fecha', y='G/P (€)', title=f"Rendimiento: {nombre}", markers=True)
        fig.update_traces(line_color='#007bff' if gp_actual >= 0 else '#dc3545')
        cols_graf[idx % 2].plotly_chart(fig, use_container_width=True)

    # Gráfico de Tarta Final
    st.divider()
    st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución Actual del Patrimonio", hole=0.4), use_container_width=True)
