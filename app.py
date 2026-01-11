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

# --- 2. CSS PARA DISEÑO PROFESIONAL ---
st.markdown("""
    <style>
    .main { background-color: #f9fafb; }
    .metric-container { display: flex; gap: 20px; margin-bottom: 25px; }
    .custom-card {
        flex: 1; padding: 22px; border-radius: 12px; height: 140px;
        display: flex; flex-direction: column; justify-content: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; background-color: white;
    }
    .highlight-card { background-color: #111827; color: white; border: none; }
    .card-label { font-size: 0.85rem; font-weight: 500; text-transform: uppercase; color: #6b7280; margin-bottom: 8px; }
    .highlight-card .card-label { color: #9ca3af; }
    .card-value { font-size: 1.85rem; font-weight: 700; color: #111827; display: flex; align-items: baseline; gap: 12px; }
    .highlight-card .card-value { color: white; }
    .pct-badge { font-size: 1.3rem; font-weight: 600; }
    .pct-pos { color: #4ade80; } 
    .pct-neg { color: #f87171; } 
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; background-color: transparent !important; }
    .stButton>button { border-radius: 6px; font-weight: 500; }
    h1, h2, h3 { color: #111827; font-weight: 700 !important; }
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
    
    # --- 4. FUNCIONES DE APOYO ---
    def resaltar_beneficio(val):
        try:
            if isinstance(val, str):
                clean_num = re.sub(r'[^0-9.\-]', '', val.split('(')[0].replace(',', ''))
                num = float(clean_num)
            else:
                num = float(val)
            if num >= 0: return 'background-color: #ecfdf5; color: #065f46; font-weight: bold;'
            else: return 'background-color: #fef2f2; color: #991b1b; font-weight: bold;'
        except: pass
        return None

    def fmt_dual(valor_eur, moneda, tasa, decimales=2):
        try:
            v_eur = float(valor_eur)
            t = float(tasa)
        except: return "N/A"
        if moneda == "USD":
            v_usd = v_eur * t
            return f"{v_eur:,.{decimales}f} € ({v_usd:,.2f} $)"
        return f"{v_eur:,.{decimales}f} €"

    # --- 5. BASES DE DATOS (CONSOLIDADO CON DOCUMENTOS) ---
    def cargar_datos_maestros():
        f_ini = "08/01/2026 11:30"
        return [
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD", "Ult_Val": f_ini},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50, "Moneda": "USD", "Ult_Val": f_ini},
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR", "Ult_Val": f_ini}
        ]

    def cargar_diario_operaciones():
        # Reconstrucción fiel según los informes detallados recibidos
        return [
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "Suscripción Inicial", "Importe": 80221.68, "Detalle": "Compra inicial 896,73 part."},
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "Beneficio Traspasado", "Importe": 2230.82, "Detalle": "Plusvalía acumulada consolidada"},
            {"Fecha": "2024-10-14", "Producto": "DWS Floating Rate", "Operación": "Suscripción nueva", "Importe": 600.44, "Detalle": "Compra 6,69 part."},
            {"Fecha": "2024-11-26", "Producto": "DWS Floating Rate", "Operación": "TRASPASO SALIDA", "Importe": -9999.96, "Detalle": "Hacia JPM US Short Duration"},
            {"Fecha": "2024-11-26", "Producto": "DWS Floating Rate", "Operación": "TRASPASO SALIDA", "Importe": -7000.00, "Detalle": "Hacia Evli Nordic Corp"},
            {"Fecha": "2024-11-26", "Producto": "Evli Nordic Corp", "Operación": "TRASPASO ENTRADA", "Importe": 7000.00, "Detalle": "Desde DWS Floating Rate"},
            {"Fecha": "2024-11-27", "Producto": "Evli Nordic Corp", "Operación": "Suscripción nueva", "Importe": 3000.00, "Detalle": "Compra 19,60 part."},
            {"Fecha": "2024-11-27", "Producto": "JPM US Short Duration", "Operación": "TRASPASO ENTRADA", "Importe": 9999.96, "Detalle": "Desde DWS Floating Rate"},
            {"Fecha": "2025-02-05", "Producto": "Numantia Patrimonio", "Operación": "Suscripción", "Importe": 5000.00, "Detalle": "Compra 203,10 part."},
            {"Fecha": "2025-02-19", "Producto": "MSCI World Index", "Operación": "Suscripción", "Importe": 5000.00, "Detalle": "Compra 415,06 part."},
            {"Fecha": "2025-02-19", "Producto": "MSCI World Index", "Operación": "Suscripción", "Importe": 16.20, "Detalle": "Compra 1,33 part."},
            {"Fecha": "2025-03-04", "Producto": "Numantia Patrimonio", "Operación": "Suscripción", "Importe": 500.00, "Detalle": "Compra 21,82 part."},
            {"Fecha": "2025-04-10", "Producto": "Numantia Patrimonio", "Operación": "Suscripción", "Importe": 500.00, "Detalle": "Compra 25,24 part."},
            {"Fecha": "2025-09-02", "Producto": "UnitedHealth", "Operación": "Compra", "Importe": 1867.84, "Detalle": "7 títulos a 309,10 US$"},
            {"Fecha": "2025-09-02", "Producto": "Numantia Patrimonio", "Operación": "Suscripción", "Importe": 1000.00, "Detalle": "Compra 41,58 part."},
            {"Fecha": "2025-09-16", "Producto": "JD.com", "Operación": "Compra", "Importe": 1710.79, "Detalle": "58 títulos a 34,82 US$"},
            {"Fecha": "2025-09-22", "Producto": "N. Exp. Textil", "Operación": "Compra", "Importe": 1043.75, "Detalle": "1.580 títulos a 0,66€"},
            {"Fecha": "2025-09-30", "Producto": "Numantia Patrimonio", "Operación": "Suscripción", "Importe": 451.82, "Detalle": "Compra 18,38 part."},
            {"Fecha": "2025-10-09", "Producto": "N. Exp. Textil", "Operación": "Compra", "Importe": 1018.05, "Detalle": "1.290 títulos a 0,79€"},
            {"Fecha": "2026-01-05", "Producto": "Amper", "Operación": "Compra", "Importe": 2023.79, "Detalle": "10.400 títulos a 0,194€"},
            {"Fecha": "2026-01-08", "Producto": "JPM US Short Duration", "Operación": "VENTA TOTAL", "Importe": -554.34, "Detalle": "Cierre de posición con pérdida consolidada."}
        ]

    def cargar_datos_aportaciones():
        return [
            {"Titular": "Ander", "Broker": "R4", "Fecha": date(2024, 8, 30), "Importe": 44000.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": date(2024, 8, 30), "Importe": 30000.0}
        ]

    # --- 6. GESTIÓN DE ARCHIVOS ---
    ARCHIVO_CSV = "cartera_final_aguirre_uranga.csv"
    ARCHIVO_AP = "aportaciones_familiares.csv"

    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except: st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())

    if 'df_aportaciones' not in st.session_state:
        try: 
            st.session_state.df_aportaciones = pd.read_csv(ARCHIVO_AP)
            st.session_state.df_aportaciones['Fecha'] = pd.to_datetime(st.session_state.df_aportaciones['Fecha']).dt.date
        except: st.session_state.df_aportaciones = pd.DataFrame(cargar_datos_aportaciones())

    # --- 7. BARRA LATERAL (SINCRONIZACIÓN CORREGIDA) ---
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
                st.toast("Actualizado", icon="✅")
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")

    # --- 8. DASHBOARD ---
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
                <div class="card-value">{ben_t:,.2f} € <span class="pct-badge {"pct-pos" if rent_t >= 0 else "pct-neg"}">{rent_t:+.2f}%</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 9. TABLAS ---
    def mostrar(tit, tipo, icon):
        st.subheader(f"{icon} {tit}")
        sub = df_v[df_v['Tipo'] == tipo].copy()
        res = sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Valor Mercado':'sum','P_Act':'first', 'Beneficio':'sum', 'Ult_Val':'first'}).reset_index()
        res['Rentabilidad %'] = (res['Beneficio'] / res['Coste'] * 100)
        res['Precio Actual'] = res.apply(lambda x: fmt_dual(x['P_Act'], x['Moneda'], rt, 4), axis=1)
        res['Beneficio (€/$)'] = res.apply(lambda x: fmt_dual(x['Beneficio'], x['Moneda'], rt), axis=1)
        res['Rentabilidad (%)'] = res['Rentabilidad %'].apply(lambda x: f"{x:.2f}%")
        with st.container(border=True):
            st.dataframe(
                res[['Broker', 'Nombre', 'Cant', 'Coste', 'Valor Mercado', 'Precio Actual', 'Beneficio (€/$)', 'Rentabilidad (%)', 'Ult_Val']]
                .style.map(resaltar_beneficio, subset=['Beneficio (€/$)', 'Rentabilidad (%)'])
                .format({"Coste":"{:.2f} €","Valor Mercado":"{:.2f} €"}),
                use_container_width=True, hide_index=True
            )

    mostrar("Acciones", "Acción", "📈")
    mostrar("Fondos", "Fondo", "📊")

    # --- 10. DIARIO Y APORTACIONES ---
    st.divider()
    col_d, col_a = st.columns([1.5, 1])
    with col_d:
        st.subheader("📜 Diario de Operaciones (Fiel a Informes)")
        df_ops = pd.DataFrame(cargar_diario_operaciones()).sort_values(by='Fecha', ascending=False)
        st.dataframe(df_ops, use_container_width=True, hide_index=True)
    with col_a:
        st.subheader("👥 Capital Aportado")
        df_ap = st.session_state.df_aportaciones.copy()
        e_ap = st.data_editor(df_ap, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Guardar Aportaciones"):
            st.session_state.df_aportaciones = e_ap
            st.session_state.df_aportaciones.to_csv(ARCHIVO_AP, index=False)
            st.toast("Guardado")
