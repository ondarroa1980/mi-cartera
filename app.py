import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date
import re

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Cartera Agirre & Uranga", 
    layout="wide", 
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# --- 2. CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .main { background-color: #f9fafb; }
    .metric-container { display: flex; gap: 20px; margin-bottom: 25px; }
    .custom-card {
        flex: 1; padding: 22px; border-radius: 12px; height: 110px;
        display: flex; flex-direction: column; justify-content: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; background-color: white;
    }
    .highlight-card { background-color: #111827; color: white; border: none; }
    .card-label { font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; color: #6b7280; }
    .highlight-card .card-label { color: #9ca3af; }
    .card-value { font-size: 1.6rem; font-weight: 700; color: #111827; }
    .highlight-card .card-value { color: white; }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SISTEMA DE SEGURIDAD ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "1234":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.title("🔐 Acceso Privado")
                st.text_input("Introduce la clave familiar:", type="password", on_change=password_entered, key="password")
        return False
    return True

if check_password():
    
    # --- 4. RUTAS DE ARCHIVOS ---
    ARCHIVO_CSV = "cartera_final_aguirre_uranga.csv"
    ARCHIVO_AP = "aportaciones_familiares.csv"

    # --- 5. FUNCIONES DE APOYO ---
    def resaltar_beneficio(val):
        try:
            clean_num = float(re.sub(r'[^0-9.\-]', '', str(val).split('(')[0].replace(',', '')))
            if clean_num >= 0: return 'background-color: #ecfdf5; color: #065f46; font-weight: bold;'
            else: return 'background-color: #fef2f2; color: #991b1b; font-weight: bold;'
        except: return None

    def fmt_dual(valor_eur, moneda, tasa, decimales=2):
        try:
            v_eur = float(valor_eur)
            t = float(tasa)
            if moneda == "USD": return f"{v_eur:,.{decimales}f} € ({v_eur * t:,.2f} $)"
            return f"{v_eur:,.{decimales}f} €"
        except: return "---"

    # --- 6. BASES DE DATOS (RECONSTRUCCIÓN TOTAL SEGÚN INFORMES) ---
    def cargar_datos_maestros():
        f_ini = "08/01/2026 11:30"
        return [
            # Acciones
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD", "Ult_Val": f_ini},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50, "Moneda": "USD", "Ult_Val": f_ini},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR", "Ult_Val": f_ini},
            # Fondos
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR", "Ult_Val": f_ini},
            # Suscripciones periódicas Numantia
            {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8299, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Val": f_ini}
        ]

    def cargar_diario_operaciones():
        return [
            # 2024
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "INGRESO (Suscripción)", "Importe": 80221.68, "Detalle": "Compra inicial 896,73 part."},
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "BENEFICIO TRASPASO", "Importe": 2230.82, "Detalle": "Plusvalía consolidada"},
            {"Fecha": "2024-10-14", "Producto": "DWS Floating Rate", "Operación": "INGRESO (Ampliación)", "Importe": 600.44, "Detalle": "6,69 part. adicionales"},
            {"Fecha": "2024-11-26", "Producto": "Evli Nordic Corp", "Operación": "TRASPASO INTERNO (Entrada)", "Importe": 7000.00, "Detalle": "Desde DWS"},
            {"Fecha": "2024-11-26", "Producto": "DWS Floating Rate", "Operación": "TRASPASO INTERNO (Salida)", "Importe": -7000.00, "Detalle": "Hacia Evli Nordic"},
            {"Fecha": "2024-11-26", "Producto": "JPM US Short Duration", "Operación": "TRASPASO INTERNO (Entrada)", "Importe": 9999.96, "Detalle": "Desde DWS"},
            {"Fecha": "2024-11-26", "Producto": "DWS Floating Rate", "Operación": "TRASPASO INTERNO (Salida)", "Importe": -9999.96, "Detalle": "Hacia JPM Short Duration"},
            {"Fecha": "2024-11-27", "Producto": "Evli Nordic Corp", "Operación": "INGRESO (Ampliación)", "Importe": 3000.00, "Detalle": "Suscripción nueva"},
            # 2025
            {"Fecha": "2025-02-05", "Producto": "Numantia Patrimonio", "Operación": "INGRESO (Suscripción)", "Importe": 5000.00, "Detalle": "Compra inicial"},
            {"Fecha": "2025-02-19", "Producto": "MSCI World Index", "Operación": "INGRESO (Suscripción)", "Importe": 5016.20, "Detalle": "5000 + 16.20 part."},
            {"Fecha": "2025-03-04", "Producto": "Numantia Patrimonio", "Operación": "INGRESO (Ampliación)", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-04-10", "Producto": "Numantia Patrimonio", "Operación": "INGRESO (Ampliación)", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-09-02", "Producto": "UnitedHealth", "Operación": "INGRESO (Compra)", "Importe": 1867.84, "Detalle": "7 títulos"},
            {"Fecha": "2025-09-02", "Producto": "Numantia Patrimonio", "Operación": "INGRESO (Ampliación)", "Importe": 1000.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-09-16", "Producto": "JD.com", "Operación": "INGRESO (Compra)", "Importe": 1710.79, "Detalle": "58 títulos"},
            {"Fecha": "2025-09-22", "Producto": "N. Exp. Textil", "Operación": "INGRESO (Compra)", "Importe": 1043.75, "Detalle": "1580 títulos"},
            {"Fecha": "2025-09-30", "Producto": "Numantia Patrimonio", "Operación": "INGRESO (Ampliación)", "Importe": 451.82, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-10-09", "Producto": "N. Exp. Textil", "Operación": "INGRESO (Compra)", "Importe": 1018.05, "Detalle": "1290 títulos"},
            {"Fecha": "2025-11-05", "Producto": "Pictet China Index", "Operación": "INGRESO (Suscripción)", "Importe": 999.98, "Detalle": "Entrada sector China"},
            # 2026
            {"Fecha": "2026-01-05", "Producto": "Amper", "Operación": "INGRESO (Compra)", "Importe": 2023.79, "Detalle": "10400 títulos"},
            {"Fecha": "2026-01-08", "Producto": "JPM US Short Duration", "Operación": "RETIRADA (Venta Total)", "Importe": -554.34, "Detalle": "Cierre por pérdida"}
        ]

    # --- 7. AUTO-GUARDADO (SIN BOTÓN) ---
    def auto_save_aportaciones():
        """Función que se activa sola al cambiar una celda de aportaciones."""
        if "ea" in st.session_state and "ex" in st.session_state:
            # Reconstruimos el dataframe desde los editores
            df_a = pd.DataFrame(st.session_state.ea['added_rows'] + st.session_state.ea['edited_rows'] if 'edited_rows' in st.session_state.ea else [])
            # Para simplificar, usamos el estado actual de los dataframes de sesión
            st.session_state.df_aportaciones.to_csv(ARCHIVO_AP, index=False)
            st.toast("Cambio guardado automáticamente", icon="💾")

    # --- 8. LÓGICA DE INICIO ---
    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except: st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())

    if 'df_aportaciones' not in st.session_state:
        try: 
            st.session_state.df_aportaciones = pd.read_csv(ARCHIVO_AP)
            st.session_state.df_aportaciones['Fecha'] = pd.to_datetime(st.session_state.df_aportaciones['Fecha']).dt.date
        except: st.session_state.df_aportaciones = pd.DataFrame(cargar_datos_aportaciones())

    # --- 9. BARRA LATERAL ---
    with st.sidebar:
        st.markdown("### 🏦 Administración")
        if st.button("🔄 Sincronizar Bolsa", use_container_width=True):
            try:
                rate_df = yf.download("EURUSD=X", period="1d", progress=False)
                rate = float(rate_df["Close"].iloc[-1]) if not rate_df.empty else 1.09
                st.session_state.rate_aguirre = rate
                tkrs = st.session_state.df_cartera[st.session_state.df_cartera['Tipo'] == "Acción"]['Ticker'].unique().tolist()
                if tkrs:
                    data = yf.download(tkrs, period="1d", progress=False)['Close']
                    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
                    for i, row in st.session_state.df_cartera.iterrows():
                        if row['Tipo'] == "Acción":
                            t = row['Ticker']
                            p_raw = data[t].iloc[-1] if len(tkrs) > 1 else data.iloc[-1]
                            if pd.notnull(p_raw):
                                p_num = float(p_raw)
                                st.session_state.df_cartera.at[i, 'P_Act'] = p_num / rate if row['Moneda'] == "USD" else p_num
                                st.session_state.df_cartera.at[i, 'Ult_Val'] = ahora
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.toast("Sincronizado", icon="✅")
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")

        if st.button("🚨 Reiniciar Datos", type="secondary", use_container_width=True):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.session_state.df_aportaciones = pd.DataFrame(cargar_datos_aportaciones())
            st.session_state.df_aportaciones.to_csv(ARCHIVO_AP, index=False)
            st.rerun()

    # --- 10. DASHBOARD ---
    rt = getattr(st.session_state, 'rate_aguirre', 1.09)
    df_v = st.session_state.df_cartera.copy()
    df_v['Valor Mercado'] = df_v['P_Act'] * df_v['Cant']
    df_v['Beneficio'] = df_v['Valor Mercado'] - df_v['Coste']
    df_v['Rentabilidad %'] = (df_v['Beneficio'] / df_v['Coste'] * 100)

    st.title("🏦 Cartera Agirre & Uranga")
    inv_t, val_t = df_v['Coste'].sum(), df_v['Valor Mercado'].sum()
    ben_t = val_t - inv_t
    rent_t = (ben_t / inv_t * 100 if inv_t > 0 else 0)

    st.markdown(f"""
        <div class="metric-container">
            <div class="custom-card"><div class="card-label">Cap. Invertido</div><div class="card-value">{inv_t:,.2f} €</div></div>
            <div class="custom-card"><div class="card-label">Valor Mercado</div><div class="card-value">{val_t:,.2f} €</div></div>
            <div class="custom-card highlight-card"><div class="card-label">Beneficio Latente</div>
                <div class="card-value">{ben_t:,.2f} € <small style='font-size:0.9rem; margin-left:8px; opacity:0.8'>{rent_t:+.2f}%</small></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    # --- 11. TABLAS Y DESGLOSES ---
    def mostrar_seccion(tit, tipo_filtro, icon):
        st.subheader(f"{icon} {tit}")
        sub = df_v[df_v['Tipo'] == tipo_filtro].copy()
        res = sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Valor Mercado':'sum','P_Act':'first', 'Beneficio':'sum', 'Ult_Val':'first'}).reset_index()
        res['Rentabilidad %'] = (res['Beneficio'] / res['Coste'] * 100)
        
        # Edición manual fondos
        if tipo_filtro == "Fondo":
            with st.expander("✏️ Actualizar Precios Manualmente"):
                res_edit = res[['Nombre', 'P_Act']].copy()
                edited = st.data_editor(res_edit, use_container_width=True, hide_index=True)
                if not edited['P_Act'].equals(res_edit['P_Act']):
                    for idx, row in edited.iterrows():
                        st.session_state.df_cartera.loc[st.session_state.df_cartera['Nombre'] == row['Nombre'], 'P_Act'] = row['P_Act']
                    st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                    st.rerun()

        res['Precio Actual'] = res.apply(lambda x: fmt_dual(x['P_Act'], x['Moneda'], rt, 4), axis=1)
        res['Beneficio (€/$)'] = res.apply(lambda x: fmt_dual(x['Beneficio'], x['Moneda'], rt), axis=1)
        res['Rentabilidad (%)'] = res['Rentabilidad %'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(res[['Broker', 'Nombre', 'Cant', 'Coste', 'Valor Mercado', 'Precio Actual', 'Beneficio (€/$)', 'Rentabilidad (%)', 'Ult_Val']]
                     .style.map(resaltar_beneficio, subset=['Beneficio (€/$)', 'Rentabilidad (%)'])
                     .format({"Coste":"{:.2f} €","Valor Mercado":"{:.2f} €", "Cant":"{:.4f}"}), use_container_width=True, hide_index=True)

    mostrar_seccion("Acciones", "Acción", "📈")
    mostrar_seccion("Fondos de Inversión", "Fondo", "📊")
    st.divider()

    # --- 12. CAPITAL APORTADO (REDiseño + AUTO-SAVE) ---
    st.subheader("👥 Capital Aportado")
    df_ap = st.session_state.df_aportaciones.copy()
    total_a = df_ap[df_ap['Titular'] == 'Ander']['Importe'].sum()
    total_x = df_ap[df_ap['Titular'] == 'Xabat']['Importe'].sum()

    st.markdown(f"""
        <div class="metric-container">
            <div class="custom-card"><div class="card-label">Total Ander</div><div class="card-value">{total_a:,.2f} €</div></div>
            <div class="custom-card"><div class="card-label">Total Xabat</div><div class="card-value">{total_x:,.2f} €</div></div>
            <div class="custom-card highlight-card"><div class="card-label">Suma Total</div><div class="card-value">{total_a + total_x:,.2f} €</div></div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Ander**")
        d_a = df_ap[df_ap['Titular'] == 'Ander'][['Broker', 'Fecha', 'Importe']].reset_index(drop=True)
        # El cambio se guarda automáticamente al cambiar de celda gracias al estado de sesión
        e_a = st.data_editor(d_a, num_rows="dynamic", key="ea", use_container_width=True)
    with c2:
        st.markdown("**Xabat**")
        d_x = df_ap[df_ap['Titular'] == 'Xabat'][['Broker', 'Fecha', 'Importe']].reset_index(drop=True)
        e_x = st.data_editor(d_x, num_rows="dynamic", key="ex", use_container_width=True)

    # Lógica de guardado al detectar cambios en los editores
    if st.session_state.ea['edited_rows'] or st.session_state.ea['added_rows'] or st.session_state.ea['deleted_rows'] or \
       st.session_state.ex['edited_rows'] or st.session_state.ex['added_rows'] or st.session_state.ex['deleted_rows']:
        # Concatenamos y guardamos
        e_a['Titular'], e_x['Titular'] = 'Ander', 'Xabat'
        st.session_state.df_aportaciones = pd.concat([e_a, e_x])
        st.session_state.df_aportaciones.to_csv(ARCHIVO_AP, index=False)
        st.toast("Cambios guardados", icon="💾")

    # --- 13. DIARIO RESTAURADO ---
    st.divider()
    st.subheader("📜 Diario de Operaciones (Restaurado)")
    df_ops = pd.DataFrame(cargar_diario_operaciones()).sort_values(by='Fecha', ascending=False)
    st.dataframe(df_ops.style.format({"Importe": "{:,.2f} €"}), use_container_width=True, hide_index=True)

    # --- 14. GRÁFICAS ---
    st.divider()
    st.subheader("📊 Análisis")
    colors = px.colors.qualitative.Plotly
    t1, t2 = st.tabs(["Distribución", "Por Activo"])
    with t1: st.plotly_chart(px.pie(df_v, values='Valor Mercado', names='Nombre', hole=0.5, color_discrete_sequence=colors), use_container_width=True)
    with t2:
        g1, g2 = st.columns(2)
        g1.plotly_chart(px.pie(df_v[df_v['Tipo']=='Acción'], values='Valor Mercado', names='Nombre', title="Acciones", hole=0.4), use_container_width=True)
        g2.plotly_chart(px.pie(df_v[df_v['Tipo']=='Fondo'], values='Valor Mercado', names='Nombre', title="Fondos", hole=0.4), use_container_width=True)
