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

# --- 2. CSS PARA DISEÑO PROFESIONAL Y ARMONIZADO ---
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
    
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; background-color: transparent !important; }
    .stButton>button { border-radius: 6px; font-weight: 500; }
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
    
    # --- 4. FUNCIONES DE APOYO (CON FIX PARA ERROR TYPEERROR) ---
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
            # Blindaje contra valores no numéricos (Fix error captura)
            v_eur = float(valor_eur)
            t = float(tasa)
            if moneda == "USD":
                return f"{v_eur:,.{decimales}f} € ({v_eur * t:,.2f} $)"
            return f"{v_eur:,.{decimales}f} €"
        except:
            return "---"

    # --- 5. BASES DE DATOS (CONSOLIDADO CON INFORMES) ---
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
            {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR", "Ult_Val": f_ini},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR", "Ult_Val": f_ini}
        ]

    def cargar_diario_operaciones():
        return [
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "INGRESO CAPITAL", "Importe": 63822.16, "Detalle": "Compra inicial fondo"},
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "BENEFICIO TRASPASADO", "Importe": 2230.82, "Detalle": "Plusvalía histórica consolidada"},
            {"Fecha": "2024-11-26", "Producto": "Evli Nordic Corp", "Operación": "TRASPASO INTERNO", "Importe": 7000.00, "Detalle": "Desde DWS"},
            {"Fecha": "2026-01-08", "Producto": "JPM US Short Duration", "Operación": "RETIRADA (VENTA TOTAL)", "Importe": -554.34, "Detalle": "Cierre posición"}
        ]

    def cargar_datos_aportaciones():
        return [
            {"Titular": "Ander", "Broker": "R4", "Fecha": date(2024, 8, 30), "Importe": 44000.0},
            {"Titular": "Ander", "Broker": "R4", "Fecha": date(2024, 9, 3), "Importe": 3000.0},
            {"Titular": "Ander", "Broker": "R4", "Fecha": date(2024, 10, 4), "Importe": 600.0},
            {"Titular": "Ander", "Broker": "R4", "Fecha": date(2025, 1, 8), "Importe": 500.0},
            {"Titular": "Ander", "Broker": "MyInvestor", "Fecha": date(2025, 2, 7), "Importe": 2500.0},
            {"Titular": "Ander", "Broker": "MyInvestor", "Fecha": date(2025, 3, 3), "Importe": 500.0},
            {"Titular": "Ander", "Broker": "R4", "Fecha": date(2025, 4, 9), "Importe": 500.0},
            {"Titular": "Ander", "Broker": "MyInvestor", "Fecha": date(2025, 4, 30), "Importe": 500.0},
            {"Titular": "Ander", "Broker": "MyInvestor", "Fecha": date(2025, 8, 14), "Importe": 500.0},
            {"Titular": "Ander", "Broker": "MyInvestor / Acción", "Fecha": date(2025, 8, 30), "Importe": 1000.0},
            {"Titular": "Ander", "Broker": "MyInvestor / Acción", "Fecha": date(2025, 9, 17), "Importe": 1000.0},
            {"Titular": "Ander", "Broker": "MyInvestor / Acción", "Fecha": date(2025, 9, 21), "Importe": 1000.0},
            {"Titular": "Ander", "Broker": "MyInvestor / Acción", "Fecha": date(2025, 10, 9), "Importe": 500.0},
            {"Titular": "Ander", "Broker": "MyInvestor / Fondo", "Fecha": date(2025, 11, 1), "Importe": 500.0},
            {"Titular": "Ander", "Broker": "R4", "Fecha": date(2025, 12, 31), "Importe": 500.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": date(2024, 8, 30), "Importe": 30000.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": date(2024, 9, 3), "Importe": 3000.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": date(2024, 11, 21), "Importe": 3000.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": date(2025, 1, 22), "Importe": 5000.0},
            {"Titular": "Xabat", "Broker": "MyInvestor", "Fecha": date(2025, 2, 7), "Importe": 2500.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": date(2025, 3, 3), "Importe": 500.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": date(2025, 8, 30), "Importe": 1000.0},
            {"Titular": "Xabat", "Broker": "MyInvestor / Acción", "Fecha": date(2025, 8, 30), "Importe": 1000.0},
            {"Titular": "Xabat", "Broker": "MyInvestor / Acción", "Fecha": date(2025, 9, 17), "Importe": 1000.0},
            {"Titular": "Xabat", "Broker": "MyInvestor / Acción", "Fecha": date(2025, 10, 9), "Importe": 500.0},
            {"Titular": "Xabat", "Broker": "MyInvestor / Fondo", "Fecha": date(2025, 11, 1), "Importe": 500.0},
        ]

    # --- 6. GESTIÓN DE ARCHIVOS ---
    ARCHIVO_CSV = "cartera_final_aguirre_uranga.csv"
    ARCHIVO_AP = "aportaciones_familiares.csv"

    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except: st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())

    if 'df_aportaciones' not in st.session_state:
        try:
            temp_ap = pd.read_csv(ARCHIVO_AP)
            temp_ap['Fecha'] = pd.to_datetime(temp_ap['Fecha']).dt.date
            st.session_state.df_aportaciones = temp_ap
        except: st.session_state.df_aportaciones = pd.DataFrame(cargar_datos_aportaciones())

    # --- 7. BARRA LATERAL ---
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

        if st.button("🚨 Reiniciar Datos", type="secondary", use_container_width=True):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.session_state.df_aportaciones = pd.DataFrame(cargar_datos_aportaciones())
            st.session_state.df_aportaciones.to_csv(ARCHIVO_AP, index=False)
            st.toast("Datos reiniciados", icon="⚠️")
            st.rerun()

    # --- 8. DASHBOARD SUPERIOR ---
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
            <div class="custom-card"><div class="card-label">Valor de Mercado</div><div class="card-value">{val_t:,.2f} €</div></div>
            <div class="custom-card highlight-card"><div class="card-label">Beneficio Latente</div>
                <div class="card-value">{ben_t:,.2f} € <small style='font-size:0.9rem; margin-left:8px; opacity:0.8'>{rent_t:+.2f}%</small></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    # --- 9. TABLAS CON DESGLOSE Y EDITOR MANUAL ---
    def mostrar_seccion(tit, tipo_filtro, icon):
        st.subheader(f"{icon} {tit}")
        sub = df_v[df_v['Tipo'] == tipo_filtro].copy()
        res = sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Valor Mercado':'sum','P_Act':'first', 'Beneficio':'sum', 'Ult_Val':'first'}).reset_index()
        res['Rentabilidad %'] = (res['Beneficio'] / res['Coste'] * 100)

        if tipo_filtro == "Fondo":
            with st.expander("✏️ Actualizar Precios de Fondos Manualmente"):
                res_edit = res[['Nombre', 'P_Act']].copy()
                edited_df = st.data_editor(res_edit, use_container_width=True, hide_index=True, key=f"edit_{tipo_filtro}")
                if not edited_df['P_Act'].equals(res_edit['P_Act']):
                    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
                    for idx, row in edited_df.iterrows():
                        st.session_state.df_cartera.loc[st.session_state.df_cartera['Nombre'] == row['Nombre'], 'P_Act'] = row['P_Act']
                        st.session_state.df_cartera.loc[st.session_state.df_cartera['Nombre'] == row['Nombre'], 'Ult_Val'] = ahora
                    st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                    st.rerun()

        res['Precio Actual'] = res.apply(lambda x: fmt_dual(x['P_Act'], x['Moneda'], rt, 4), axis=1)
        res['Beneficio (€/$)'] = res.apply(lambda x: fmt_dual(x['Beneficio'], x['Moneda'], rt), axis=1)
        res['Rentabilidad (%)'] = res['Rentabilidad %'].apply(lambda x: f"{x:.2f}%")
        
        with st.container(border=True):
            st.dataframe(
                res[['Broker', 'Nombre', 'Cant', 'Coste', 'Valor Mercado', 'Precio Actual', 'Beneficio (€/$)', 'Rentabilidad (%)', 'Ult_Val']]
                .style.map(resaltar_beneficio, subset=['Beneficio (€/$)', 'Rentabilidad (%)'])
                .format({"Coste":"{:.2f} €","Valor Mercado":"{:.2f} €", "Cant":"{:.4f}"}),
                use_container_width=True, hide_index=True
            )

        with st.expander(f"Ver compras individuales de {tit}"):
            for n in sub['Nombre'].unique():
                det = sub[sub['Nombre'] == n].copy()
                det['Rentabilidad %'] = (det['Beneficio'] / det['Coste'] * 100)
                det['Precio Actual'] = det.apply(lambda x: fmt_dual(x['P_Act'], x['Moneda'], rt, 4), axis=1)
                det['Beneficio (€/$)'] = det.apply(lambda x: fmt_dual(x['Beneficio'], x['Moneda'], rt), axis=1)
                det['Rentabilidad (%)'] = det['Rentabilidad %'].apply(lambda x: f"{x:.2f}%")
                st.markdown(f"**{n}**")
                st.dataframe(det[['Fecha', 'Cant', 'Coste', 'Precio Actual', 'Valor Mercado', 'Beneficio (€/$)', 'Rentabilidad (%)']]
                    .style.map(resaltar_beneficio, subset=['Beneficio (€/$)', 'Rentabilidad (%)'])
                    .format({"Coste":"{:.2f} €","Valor Mercado":"{:.2f} €", "Cant":"{:.4f}"}), use_container_width=True, hide_index=True)

    mostrar_seccion("Acciones", "Acción", "📈")
    mostrar_seccion("Fondos de Inversión", "Fondo", "📊")
    st.divider()

    # --- 10. CAPITAL APORTADO (REDiseño solicitado) ---
    st.subheader("👥 Capital Aportado")
    df_ap = st.session_state.df_aportaciones.copy()
    
    # Cálculo de totales
    total_a = df_ap[df_ap['Titular'] == 'Ander']['Importe'].sum()
    total_x = df_ap[df_ap['Titular'] == 'Xabat']['Importe'].sum()
    total_global = total_a + total_x

    # Tarjetas de totales (Arriba para visibilidad)
    st.markdown(f"""
        <div class="metric-container">
            <div class="custom-card"><div class="card-label">Total Ander</div><div class="card-value">{total_a:,.2f} €</div></div>
            <div class="custom-card"><div class="card-label">Total Xabat</div><div class="card-value">{total_x:,.2f} €</div></div>
            <div class="custom-card highlight-card"><div class="card-label">Suma Total Cartera</div><div class="card-value">{total_global:,.2f} €</div></div>
        </div>
    """, unsafe_allow_html=True)

    col_a, col_x = st.columns(2)
    with col_a:
        st.markdown("**Lista Ander**")
        d_a = df_ap[df_ap['Titular'] == 'Ander'][['Broker', 'Fecha', 'Importe']].reset_index(drop=True)
        e_a = st.data_editor(d_a, num_rows="dynamic", key="ea", use_container_width=True, column_config={"Importe": st.column_config.NumberColumn(format="%.2f €")})
    with col_x:
        st.markdown("**Lista Xabat**")
        d_x = df_ap[df_ap['Titular'] == 'Xabat'][['Broker', 'Fecha', 'Importe']].reset_index(drop=True)
        e_x = st.data_editor(d_x, num_rows="dynamic", key="ex", use_container_width=True, column_config={"Importe": st.column_config.NumberColumn(format="%.2f €")})

    st.info("💡 **¿Para qué sirve el botón?** Al editar las listas superiores, los cambios solo se ven en pantalla. Pulsa 'Guardar' para grabarlos definitivamente en el archivo de la aplicación.")
    if st.button("💾 Guardar Aportaciones", use_container_width=True):
        e_a['Titular'], e_x['Titular'] = 'Ander', 'Xabat'
        st.session_state.df_aportaciones = pd.concat([e_a, e_x])
        st.session_state.df_aportaciones.to_csv(ARCHIVO_AP, index=False)
        st.toast("Datos guardados con éxito")
        st.rerun()

    # --- 11. DIARIO DE OPERACIONES ---
    st.divider()
    st.subheader("📜 Diario de Operaciones")
    df_ops = pd.DataFrame(cargar_diario_operaciones()).sort_values(by='Fecha', ascending=False)
    with st.container(border=True):
        st.dataframe(df_ops.style.format({"Importe": "{:,.2f} €"}), use_container_width=True, hide_index=True)

    # --- 12. GRÁFICAS ---
    st.divider()
    st.subheader("📊 Análisis Visual")
    colors = px.colors.qualitative.Plotly
    t1, t2 = st.tabs(["Distribución Global", "Por Tipo"])
    with t1:
        st.plotly_chart(px.pie(df_v, values='Valor Mercado', names='Nombre', hole=0.5, color_discrete_sequence=colors), use_container_width=True)
    with t2:
        g1, g2 = st.columns(2)
        g1.plotly_chart(px.pie(df_v[df_v['Tipo']=='Acción'], values='Valor Mercado', names='Nombre', title="Acciones", hole=0.4), use_container_width=True)
        g2.plotly_chart(px.pie(df_v[df_v['Tipo']=='Fondo'], values='Valor Mercado', names='Nombre', title="Fondos", hole=0.4), use_container_width=True)
