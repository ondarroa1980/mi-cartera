import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

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
    
    # --- 3. GESTIÓN DE ARCHIVOS Y DATOS INICIALES ---
    ARCHIVO_CSV = "cartera_final_aguirre_uranga.csv"
    
    def cargar_datos_maestros():
        return [
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR"},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR"},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD"},
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"}
        ]

    if 'df_cartera' not in st.session_state:
        try:
            st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    # --- 4. BARRA LATERAL (SIDEBAR) MEJORADA ---
    with st.sidebar:
        st.header("➕ Añadir Operación")
        with st.form("nuevo_activo"):
            f_fecha = st.date_input("Fecha", datetime.now())
            f_tipo = st.selectbox("Tipo", ["Acción", "Fondo"])
            f_broker = st.selectbox("Broker", ["MyInvestor", "Renta 4"])
            f_ticker = st.text_input("Ticker (ej: AAPL o ISIN)")
            f_nombre = st.text_input("Nombre del Activo")
            f_cant = st.number_input("Cantidad", min_value=0.0, step=0.01)
            f_coste = st.number_input("Inversión Total (€)", min_value=0.0, step=0.01)
            f_p_act = st.number_input("Precio Actual (Manual)", min_value=0.0, step=0.0001)
            f_moneda = st.radio("Moneda", ["EUR", "USD"])
            
            if st.form_submit_button("Guardar en Cartera"):
                nueva_fila = {
                    "Fecha": f_fecha.strftime("%Y-%m-%d"), "Tipo": f_tipo, "Broker": f_broker,
                    "Ticker": f_ticker, "Nombre": f_nombre, "Cant": f_cant,
                    "Coste": f_coste, "P_Act": f_p_act, "Moneda": f_moneda
                }
                st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, pd.DataFrame([nueva_fila])], ignore_index=True)
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.success("Activo añadido!")
                st.rerun()

        st.divider()
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            try:
                rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
                st.session_state.rate_aguirre = rate
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        p_raw = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                        st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate if row['Moneda'] == "USD" else p_raw
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Error de conexión a Yahoo Finance.")
        
        if st.button("🗑️ Borrar Cartera (Reset)"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.rerun()

    # --- 5. PROCESAMIENTO DE DATOS ---
    rt = getattr(st.session_state, 'rate_aguirre', 1.09)
    df = st.session_state.df_cartera.copy()
    df['Valor Mercado'] = df['P_Act'] * df['Cant']
    df['Beneficio (€)'] = df['Valor Mercado'] - df['Coste']
    
    # --- 6. INTERFAZ DASHBOARD ---
    st.title("🏦 Cartera Agirre & Uranga")
    
    # Métricas Principales
    total_invertido = df['Coste'].sum()
    total_mercado = df['Valor Mercado'].sum()
    total_beneficio = total_mercado - total_invertido
    rent_total = (total_beneficio / total_invertido * 100) if total_invertido > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Invertido", f"{total_invertido:,.2f} €")
    col2.metric("Valor Actual", f"{total_mercado:,.2f} €")
    col3.metric("Beneficio Total", f"{total_beneficio:,.2f} €", f"{rent_total:.2f}%")
    col4.metric("Tipo Cambio (USD/EUR)", f"{rt:.4f}")

    st.divider()

    # --- 7. VISUALIZACIÓN ---
    c_left, c_right = st.columns(2)
    
    with c_left:
        fig_pie = px.pie(df, values='Valor Mercado', names='Nombre', title="Distribución de la Cartera", hole=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c_right:
        # Gráfico Comparativo
        df_group = df.groupby('Tipo')[['Coste', 'Valor Mercado']].sum().reset_index()
        fig_bar = px.bar(df_group, x='Tipo', y=['Coste', 'Valor Mercado'], barmode='group', 
                         title="Coste vs Valor Actual por Tipo", labels={'value': 'Euros (€)'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- 8. TABLAS DETALLADAS (REUTILIZANDO TU LÓGICA DE FORMATEO) ---
    def resaltar_beneficio(val):
        if isinstance(val, (int, float)):
            color = '#d4edda' if val > 0 else '#f8d7da'
            return f'background-color: {color}'
        return None

    st.header("📋 Detalle de Posiciones")
    tabs = st.tabs(["Acciones", "Fondos de Inversión"])

    with tabs[0]:
        df_acc = df[df['Tipo'] == "Acción"]
        if not df_acc.empty:
            st.dataframe(df_acc[['Nombre', 'Ticker', 'Cant', 'Coste', 'P_Act', 'Valor Mercado', 'Beneficio (€)']]
                         .style.applymap(resaltar_beneficio, subset=['Beneficio (€)'])
                         .format({"Coste": "{:.2f}€", "P_Act": "{:.4f}", "Valor Mercado": "{:.2f}€", "Beneficio (€)": "{:.2f}€"}), 
                         use_container_width=True)

    with tabs[1]:
        df_fon = df[df['Tipo'] == "Fondo"]
        if not df_fon.empty:
            st.warning("Doble clic en 'P_Act' para actualizar el valor liquidativo manualmente.")
            edited_df = st.data_editor(df_fon[['Nombre', 'Ticker', 'Cant', 'Coste', 'P_Act', 'Valor Mercado', 'Beneficio (€)']],
                                       disabled=['Nombre', 'Ticker', 'Cant', 'Coste', 'Valor Mercado', 'Beneficio (€)'],
                                       key="editor_fondos", use_container_width=True)
            # Guardar cambios del editor manual
            if st.button("Guardar Cambios Manuales en Fondos"):
                for i, row in edited_df.iterrows():
                    st.session_state.df_cartera.loc[st.session_state.df_cartera['Ticker'] == row['Ticker'], 'P_Act'] = row['P_Act']
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.success("Precios de fondos actualizados.")
                st.rerun()
