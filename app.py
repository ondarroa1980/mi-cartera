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
    
    # --- 3. BASE DE DATOS MAESTRA (ACTIVOS VIVOS) ---
    def cargar_datos_maestros():
        return [
            # ACCIONES
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR"},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR"},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Moneda": "EUR"},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD"},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50, "Moneda": "USD"},
            # FONDOS RENTA 4
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Moneda": "EUR"},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22, "Moneda": "EUR"},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
            # FONDOS MYINVESTOR
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR"}
        ]

    # --- 4. DATOS DE APORTACIONES (NUEVO SEGÚN IMAGEN) ---
    def cargar_datos_aportaciones():
        return [
            {"Titular": "Ander", "Broker": "R4", "Fecha": "2024-08-30", "Importe": 44000.0},
            {"Titular": "Ander", "Broker": "R4", "Fecha": "2024-09-03", "Importe": 3000.0},
            {"Titular": "Ander", "Broker": "R4", "Fecha": "2024-10-04", "Importe": 600.0},
            {"Titular": "Ander", "Broker": "R4", "Fecha": "2025-01-08", "Importe": 500.0},
            {"Titular": "Ander", "Broker": "MyInvestor", "Fecha": "2025-02-07", "Importe": 2500.0},
            {"Titular": "Ander", "Broker": "MyInvestor", "Fecha": "2025-03-03", "Importe": 500.0},
            {"Titular": "Ander", "Broker": "R4", "Fecha": "2025-04-09", "Importe": 500.0},
            {"Titular": "Ander", "Broker": "MyInvestor", "Fecha": "2025-04-30", "Importe": 500.0},
            {"Titular": "Ander", "Broker": "MyInvestor", "Fecha": "2025-08-14", "Importe": 500.0},
            {"Titular": "Ander", "Broker": "MyInvestor / Acción", "Fecha": "2025-08-30", "Importe": 1000.0},
            {"Titular": "Ander", "Broker": "MyInvestor / Acción", "Fecha": "2025-09-17", "Importe": 1000.0},
            {"Titular": "Ander", "Broker": "MyInvestor / Acción", "Fecha": "2025-09-21", "Importe": 1000.0},
            {"Titular": "Ander", "Broker": "MyInvestor / Acción", "Fecha": "2025-10-09", "Importe": 500.0},
            {"Titular": "Ander", "Broker": "MyInvestor / Fondo", "Fecha": "2025-11-01", "Importe": 500.0},
            {"Titular": "Ander", "Broker": "R4", "Fecha": "2025-12-31", "Importe": 500.0},
            # XABAT
            {"Titular": "Xabat", "Broker": "R4", "Fecha": "2024-08-30", "Importe": 30000.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": "2024-09-03", "Importe": 3000.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": "2024-11-21", "Importe": 3000.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": "2025-01-22", "Importe": 5000.0},
            {"Titular": "Xabat", "Broker": "MyInvestor", "Fecha": "2025-02-07", "Importe": 2500.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": "2025-03-03", "Importe": 500.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": "2025-08-30", "Importe": 1000.0},
            {"Titular": "Xabat", "Broker": "MyInvestor / Acción", "Fecha": "2025-08-30", "Importe": 1000.0},
            {"Titular": "Xabat", "Broker": "MyInvestor / Acción", "Fecha": "2025-09-17", "Importe": 1000.0},
            {"Titular": "Xabat", "Broker": "MyInvestor / Acción", "Fecha": "2025-10-09", "Importe": 500.0},
            {"Titular": "Xabat", "Broker": "MyInvestor / Fondo", "Fecha": "2025-11-01", "Importe": 500.0},
        ]

    # --- 5. GESTIÓN DE ARCHIVOS ---
    ARCHIVO_CSV = "cartera_final_aguirre_uranga.csv"
    ARCHIVO_APORTACIONES = "aportaciones_familiares.csv"

    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    if 'df_aportaciones' not in st.session_state:
        try: st.session_state.df_aportaciones = pd.read_csv(ARCHIVO_APORTACIONES)
        except:
            st.session_state.df_aportaciones = pd.DataFrame(cargar_datos_aportaciones())
            st.session_state.df_aportaciones.to_csv(ARCHIVO_APORTACIONES, index=False)

    # --- 6. BARRA LATERAL (SINCRONIZACIÓN MEJORADA) ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            success_count = 0
            fail_tickers = []
            try:
                exchange_data = yf.Ticker("EURUSD=X").history(period="1d")
                rate = exchange_data["Close"].iloc[-1] if not exchange_data.empty else 1.09
                st.session_state.rate_aguirre = rate
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        try:
                            ticker_data = yf.Ticker(row['Ticker']).history(period="1d")
                            if not ticker_data.empty:
                                p_raw = ticker_data["Close"].iloc[-1]
                                st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate if row['Moneda'] == "USD" else p_raw
                                success_count += 1
                        except: fail_tickers.append(row['Ticker'])
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Error de conexión.")
        
        if st.button("🚨 Reiniciar Todo"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.session_state.df_aportaciones = pd.DataFrame(cargar_datos_aportaciones())
            st.session_state.df_aportaciones.to_csv(ARCHIVO_APORTACIONES, index=False)
            st.rerun()

    # --- 7. DASHBOARD SUPERIOR ---
    st.title("🏦 Cartera Agirre & Uranga")
    
    df_vivos = st.session_state.df_cartera.copy()
    df_vivos = df_vivos[df_vivos['Nombre'] != "JPM US Short Duration"]
    df_vivos['Valor Mercado'] = df_vivos['P_Act'] * df_vivos['Cant']
    df_vivos['Beneficio'] = df_vivos['Valor Mercado'] - df_vivos['Coste']
    
    t_inv = df_vivos['Coste'].sum()
    t_val = df_vivos['Valor Mercado'].sum()
    t_ben = t_val - t_inv

    m1, m2, m3 = st.columns(3)
    m1.metric("Dinero Invertido (Vivos)", f"{t_inv:,.2f} €")
    m2.metric("Valor Actual Cartera", f"{t_val:,.2f} €")
    m3.metric("Beneficio TOTAL VIVO", f"{t_ben:,.2f} €", f"{(t_ben/t_inv*100):.2f}%")
    st.divider()

    # --- 8. SECCIÓN APORTACIONES (NUEVA TABLA EDITABLE) ---
    st.header("📑 Aportaciones Familiares (R4 + MyInvestor)")
    st.write("Gestiona aquí cuánto dinero ha puesto cada titular en los bancos.")

    # Separamos los datos para Ander y Xabat
    df_ap = st.session_state.df_aportaciones.copy()
    
    col_ander, col_xabat = st.columns(2)

    with col_ander:
        st.subheader("👨‍💼 ANDER")
        df_ander = df_ap[df_ap['Titular'] == 'Ander'][['Broker', 'Fecha', 'Importe']].reset_index(drop=True)
        edited_ander = st.data_editor(
            df_ander, 
            num_rows="dynamic", 
            key="edit_ander",
            use_container_width=True,
            column_config={
                "Importe": st.column_config.NumberColumn(format="%.2f €"),
                "Fecha": st.column_config.DateColumn()
            }
        )
        total_a = edited_ander['Importe'].sum()
        st.info(f"**TOTAL ANDER: {total_a:,.2f} €**")

    with col_xabat:
        st.subheader("👨‍💼 XABAT")
        df_xabat = df_ap[df_ap['Titular'] == 'Xabat'][['Broker', 'Fecha', 'Importe']].reset_index(drop=True)
        edited_xabat = st.data_editor(
            df_xabat, 
            num_rows="dynamic", 
            key="edit_xabat",
            use_container_width=True,
            column_config={
                "Importe": st.column_config.NumberColumn(format="%.2f €"),
                "Fecha": st.column_config.DateColumn()
            }
        )
        total_x = edited_xabat['Importe'].sum()
        st.info(f"**TOTAL XABAT: {total_x:,.2f} €**")

    # Guardar cambios si se detectan
    if st.button("💾 Guardar Aportaciones"):
        edited_ander['Titular'] = 'Ander'
        edited_xabat['Titular'] = 'Xabat'
        final_aportaciones = pd.concat([edited_ander, edited_xabat])
        st.session_state.df_aportaciones = final_aportaciones
        st.session_state.df_aportaciones.to_csv(ARCHIVO_APORTACIONES, index=False)
        st.success("Aportaciones guardadas correctamente.")
        st.rerun()

    # Métrica de suma total de aportaciones
    st.markdown(f"""
    <div style="text-align: center; background-color: #ffeb3b; padding: 10px; border-radius: 10px; color: black; font-size: 24px; font-weight: bold;">
        SUMA TOTAL APORTADO: {total_a + total_x:,.2f} €
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # --- 9. GRÁFICAS DE PESOS ---
    st.header("📊 Distribución de Cartera")
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(px.pie(df_vivos[df_vivos['Tipo']=='Acción'], values='Valor Mercado', names='Nombre', title="Pesos en Acciones", hole=0.3), use_container_width=True)
    with g2:
        st.plotly_chart(px.pie(df_vivos[df_vivos['Tipo']=='Fondo'], values='Valor Mercado', names='Nombre', title="Pesos en Fondos", hole=0.3), use_container_width=True)
    st.divider()

    # --- 10. DETALLE DE POSICIONES VIVAS ---
    def resaltar(val):
        if isinstance(val, str) and "€" in val:
            try:
                n = float(val.split("€")[0].replace(",","").strip())
                return 'background-color: #d4edda' if n > 0 else 'background-color: #f8d7da'
            except: pass
        return None

    def mostrar_seccion(titulo, filtro):
        st.header(f"💼 {titulo}")
        df_sub = df_vivos[df_vivos['Tipo'] == filtro].copy()
        res = df_sub.groupby(['Nombre', 'Broker']).agg({'Cant':'sum','Coste':'sum','Valor Mercado':'sum','P_Act':'first'}).reset_index()
        res['Beneficio (€)'] = res['Valor Mercado'] - res['Coste']
        res['Rent. %'] = (res['Beneficio (€)'] / res['Coste'] * 100)
        
        st.dataframe(
            res.style.applymap(resaltar, subset=['Beneficio (€)']).format({"Coste":"{:.2f} €","Valor Mercado":"{:.2f} €","Beneficio (€)":"{:.2f} €","Rent. %":"{:.2f}%"}), 
            use_container_width=True
        )
        
        for n in df_sub['Nombre'].unique():
            with st.expander(f"Ver historial: {n}"):
                st.table(df_sub[df_sub['Nombre']==n][['Fecha','Cant','Coste','P_Act','Beneficio']])

    mostrar_seccion("Acciones", "Acción")
    mostrar_seccion("Fondos de Inversión", "Fondo")
