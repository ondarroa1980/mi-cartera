import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Agirre & Uranga | Wealth Management", layout="wide", page_icon="🏦")

# Inyección de CSS para un diseño sofisticado
st.markdown("""
    <style>
    /* Estilo general */
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: white;
        padding: 20px !important;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
    }
    /* Badges de Broker */
    .badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: bold;
        color: white;
    }
    .my-investor { background-color: #0046ff; }
    .renta-4 { background-color: #ff4b4b; }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

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

    # --- 3. FUNCIONES DE APOYO ---
    def resaltar_beneficio(val):
        try:
            if isinstance(val, str):
                num = float(val.split(' ')[0].replace(',', ''))
            else: num = val
            if num > 0: return 'background-color: #e6fffa; color: #234e52; font-weight: bold;'
            if num < 0: return 'background-color: #fff5f5; color: #822727; font-weight: bold;'
        except: pass
        return None

    def fmt_dual(valor_eur, moneda, tasa, decimales=2):
        if moneda == "USD":
            return f"{valor_eur:,.{decimales}f} € ({valor_eur * tasa:,.2f} $)"
        return f"{valor_eur:,.{decimales}f} €"

    # --- 4. BASES DE DATOS (Mismos datos) ---
    def cargar_datos_maestros():
        return [
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR"},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR"},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Moneda": "EUR"},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD"},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50, "Moneda": "USD"},
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Moneda": "EUR"},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22, "Moneda": "EUR"},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR"}
        ]
    
    # Diario y Aportaciones (mantener igual que el original del usuario...)
    def cargar_diario_operaciones():
        return [{"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "Compra inicial", "Importe": 63822.16, "Detalle": "Entrada fondo monetario"}] # Resumido para el ejemplo

    # --- 5. GESTIÓN DE ARCHIVOS ---
    ARCHIVO_CSV = "cartera_final_aguirre_uranga.csv"
    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except: st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())

    # --- 6. BARRA LATERAL (CON API TOTAL) ---
    with st.sidebar:
        st.header("⚙️ Centro de Control")
        if st.button("🔄 Sincronizar Cotizaciones", use_container_width=True):
            with st.spinner("Conectando con Yahoo Finance..."):
                try:
                    rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
                    st.session_state.rate_aguirre = rate
                    # Sincroniza tanto Acciones como Fondos por su Ticker/ISIN
                    for i, row in st.session_state.df_cartera.iterrows():
                        t_data = yf.Ticker(row['Ticker']).history(period="1d")
                        if not t_data.empty:
                            p_raw = t_data["Close"].iloc[-1]
                            st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate if row['Moneda'] == "USD" else p_raw
                    st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                    st.success("Cartera Actualizada")
                    st.rerun()
                except: st.error("Error de conexión API.")

    # --- 7. PROCESAMIENTO Y HACIENDA ---
    rt = getattr(st.session_state, 'rate_aguirre', 1.09)
    df_v = st.session_state.df_cartera.copy()
    df_v['Valor Mercado'] = df_v['P_Act'] * df_v['Cant']
    df_v['Beneficio'] = df_v['Valor Mercado'] - df_v['Coste']
    
    # Cálculo Hacienda (19% de retención sobre plusvalía)
    df_v['Beneficio Neto'] = df_v['Beneficio'].apply(lambda x: x * 0.81 if x > 0 else x)
    df_v['Rent %'] = (df_v['Beneficio'] / df_v['Coste'] * 100)

    # --- 8. DASHBOARD SUPERIOR ---
    st.title("🏦 Wealth Management | Agirre & Uranga")
    
    inv_total = df_v['Coste'].sum()
    val_total = df_v['Valor Mercado'].sum()
    ben_total = val_total - inv_total
    ben_neto = df_v['Beneficio Neto'].sum()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Capital Invertido", f"{inv_total:,.2f} €")
    m2.metric("Valor de Mercado", f"{val_total:,.2f} €")
    m3.metric("Beneficio Bruto", f"{ben_total:,.2f} €", f"{(ben_total/inv_total*100):.2f}%")
    m4.metric("Neto (IRPF 19%)", f"{ben_neto:,.2f} €", help="Beneficio tras impuestos")

    # --- 9. TABS PARA ORGANIZACIÓN ---
    tab_inv, tab_ops, tab_vis = st.tabs(["📈 Mi Cartera", "📜 Operaciones", "📊 Análisis"])

    with tab_inv:
        def render_tabla(tipo):
            sub = df_v[df_v['Tipo'] == tipo].copy()
            res = sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({
                'Cant':'sum','Coste':'sum','Valor Mercado':'sum','P_Act':'first', 'Beneficio':'sum', 'Beneficio Neto':'sum'
            }).reset_index()
            
            res['Rent %'] = (res['Beneficio'] / res['Coste'] * 100)
            res['Precio'] = res.apply(lambda x: fmt_dual(x['P_Act'], x['Moneda'], rt, 4), axis=1)
            res['Ganancia €'] = res.apply(lambda x: fmt_dual(x['Beneficio'], x['Moneda'], rt), axis=1)
            res['Neto €'] = res['Beneficio Neto'].map("{:,.2f} €".format)

            st.dataframe(
                res[['Broker', 'Nombre', 'Coste', 'Valor Mercado', 'Precio', 'Ganancia €', 'Neto €', 'Rent %']]
                .style.applymap(resaltar_beneficio, subset=['Ganancia €', 'Neto €', 'Rent %'])
                .format({"Coste":"{:,.2f} €","Valor Mercado":"{:,.2f} €","Rent %":"{:.2f}%"}),
                use_container_width=True, hide_index=True
            )

        st.subheader("Acciones")
        render_tabla("Acción")
        st.subheader("Fondos de Inversión")
        render_tabla("Fondo")

    with tab_vis:
        c_left, c_right = st.columns(2)
        with c_left:
            st.plotly_chart(px.sunburst(df_v, path=['Broker', 'Tipo', 'Nombre'], values='Valor Mercado', 
                                       title="Jerarquía de Inversión", color_continuous_scale='RdYlGn'), use_container_width=True)
        with c_right:
            st.plotly_chart(px.bar(df_v.groupby('Nombre')['Beneficio'].sum().reset_index(), 
                                   x='Nombre', y='Beneficio', title="Beneficio por Activo", color='Beneficio'), use_container_width=True)

    # --- 11. PIE DE PÁGINA ---
    st.markdown("---")
    st.caption(f"Última actualización de mercados: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Tasa EUR/USD: {rt:.4f}")
