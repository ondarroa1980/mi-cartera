import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO ---
st.set_page_config(page_title="Agirre & Uranga | Wealth Management", layout="wide", page_icon="🏦")

# CSS personalizado para mejorar la estética
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .broker-badge { padding: 4px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    .myinvestor { background-color: #e3f2fd; color: #1976d2; }
    .renta4 { background-color: #fff3e0; color: #e65100; }
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

    # --- 3. LÓGICA DE IMPUESTOS Y ESTILOS ---
    def calcular_neto(row):
        """Calcula el beneficio neto tras el 19% de IRPF sobre plusvalías."""
        bruto = row['Beneficio']
        if bruto > 0:
            return bruto * 0.81  # Retención del 19%
        return bruto # Las pérdidas no se gravan

    def resaltar_beneficio(val):
        try:
            if isinstance(val, str):
                clean_val = val.split(' ')[0].replace(',', '')
                num = float(clean_val)
            else: num = val
            if num > 0: return 'color: #2e7d32; background-color: #e8f5e9; font-weight: bold;'
            if num < 0: return 'color: #c62828; background-color: #ffebee; font-weight: bold;'
        except: pass
        return None

    def fmt_dual(valor_eur, moneda, tasa, decimales=2):
        if moneda == "USD":
            return f"{valor_eur:,.{decimales}f} € ({valor_eur * tasa:,.2f} $)"
        return f"{valor_eur:,.{decimales}f} €"

    # --- 4. BASES DE DATOS (Mantenemos tus datos originales) ---
    def cargar_datos_maestros():
        return [
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR"},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR"},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD"},
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR"},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"}
        ]

    # Gestión de archivos (CSV)
    ARCHIVO_CSV = "cartera_final_aguirre_uranga.csv"
    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except: st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())

    # --- 5. BARRA LATERAL CON LOGOS ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135706.png", width=100) # Logo genérico gestión
        st.header("⚙️ Operaciones")
        
        if st.button("🔄 Sincronizar (Acciones y Fondos)"):
            with st.spinner("Actualizando cotizaciones..."):
                try:
                    # Tasa de cambio
                    rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
                    st.session_state.rate_aguirre = rate
                    
                    for i, row in st.session_state.df_cartera.iterrows():
                        # yf.Ticker funciona con la mayoría de ISINs y Tickers de Yahoo
                        t_data = yf.Ticker(row['Ticker']).history(period="1d")
                        if not t_data.empty:
                            p_raw = t_data["Close"].iloc[-1]
                            # Ajuste si es moneda extranjera
                            st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate if row['Moneda'] == "USD" else p_raw
                    
                    st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                    st.success("Sincronización completa")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- 6. PROCESAMIENTO DE DATOS ---
    rt = getattr(st.session_state, 'rate_aguirre', 1.09)
    df_v = st.session_state.df_cartera.copy()
    
    # Cálculos Financieros
    df_v['Valor Mercado'] = df_v['P_Act'] * df_v['Cant']
    df_v['Beneficio'] = df_v['Valor Mercado'] - df_v['Coste']
    df_v['Beneficio Neto'] = df_v.apply(calcular_neto, axis=1)
    df_v['Rent %'] = (df_v['Beneficio'] / df_v['Coste'] * 100)

    # --- 7. DASHBOARD SUPERIOR ---
    st.title("💰 Wealth Management Agirre & Uranga")
    
    inv_total = df_v['Coste'].sum()
    val_total = df_v['Valor Mercado'].sum()
    ben_bruto = val_total - inv_total
    ben_neto = df_v['Beneficio Neto'].sum()
    
    # Tarjetas de métricas estilizadas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capital Invertido", f"{inv_total:,.2f} €")
    c2.metric("Valor de Mercado", f"{val_total:,.2f} €")
    c3.metric("Beneficio Bruto", f"{ben_bruto:,.2f} €", f"{(ben_bruto/inv_total*100):.2f}%")
    c4.metric("Beneficio Neto (IRPF)", f"{ben_neto:,.2f} €", help="Tras aplicar 19% de impuestos sobre ganancias")

    st.divider()

    # --- 8. TABLAS DETALLADAS ---
    def mostrar_seccion(tit, tipo_filtro):
        st.subheader(tit)
        sub = df_v[df_v['Tipo'] == tipo_filtro].copy()
        
        # Agregación para visualización
        res = sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({
            'Cant':'sum','Coste':'sum','Valor Mercado':'sum','P_Act':'first', 
            'Beneficio':'sum', 'Beneficio Neto': 'sum'
        }).reset_index()
        
        res['Rent %'] = (res['Beneficio'] / res['Coste'] * 100)
        res['Precio'] = res.apply(lambda x: fmt_dual(x['P_Act'], x['Moneda'], rt, 4), axis=1)
        res['Ganancia €'] = res['Beneficio'].map("{:,.2f} €".format)
        res['Ganancia Neta (19%)'] = res['Beneficio Neto'].map("{:,.2f} €".format)

        st.dataframe(
            res[['Broker', 'Nombre', 'Coste', 'Valor Mercado', 'Precio', 'Ganancia €', 'Ganancia Neta (19%)', 'Rent %']]
            .style.applymap(resaltar_beneficio, subset=['Ganancia €', 'Ganancia Neta (19%)', 'Rent %'])
            .format({"Coste":"{:.2f} €","Valor Mercado":"{:.2f} €","Rent %":"{:.2f}%"}),
            use_container_width=True, hide_index=True
        )

    mostrar_seccion("📈 Cartera de Acciones", "Acción")
    mostrar_seccion("펀 Fondos de Inversión", "Fondo")

    # --- 9. GRÁFICO DE DISTRIBUCIÓN ---
    st.divider()
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.plotly_chart(px.pie(df_v, values='Valor Mercado', names='Broker', title="Distribución por Broker", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
    with col_chart2:
        st.plotly_chart(px.bar(df_v, x='Nombre', y='Beneficio Neto', title="Beneficio Neto por Activo", color='Beneficio Neto', color_continuous_scale='RdYlGn'), use_container_width=True)
