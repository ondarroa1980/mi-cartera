import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date

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
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
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
                clean_val = val.split(' ')[0].replace(',', '')
                num = float(clean_val)
            elif isinstance(val, (int, float)):
                num = val
            else: return None
            if num > 0: return 'background-color: #ecfdf5; color: #065f46; font-weight: bold;'
            if num < 0: return 'background-color: #fef2f2; color: #991b1b; font-weight: bold;'
        except: pass
        return None

    def fmt_dual(valor_eur, moneda, tasa, decimales=2):
        if moneda == "USD":
            valor_usd = valor_eur * tasa
            return f"{valor_eur:,.{decimales}f} € ({valor_usd:,.2f} $)"
        return f"{valor_eur:,.{decimales}f} €"

    # --- 5. BASES DE DATOS ---
    def cargar_datos_maestros():
        # Se añade el campo 'Ult_Act' para rastrear la última valoración
        f_init = datetime.now().strftime("%d/%m/%Y %H:%M")
        return [
            {"Fecha": "2026-01-05", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cant": 10400.0, "Coste": 2023.79, "P_Act": 0.194, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2025-09-22", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1580.0, "Coste": 1043.75, "P_Act": 0.718, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2025-10-09", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cant": 1290.0, "Coste": 1018.05, "P_Act": 0.718, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2025-09-02", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cant": 7.0, "Coste": 1867.84, "P_Act": 266.83, "Moneda": "USD", "Ult_Act": f_init},
            {"Fecha": "2025-09-16", "Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cant": 58.0, "Coste": 1710.79, "P_Act": 29.50, "Moneda": "USD", "Ult_Act": f_init},
            {"Fecha": "2024-09-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "LU0034353002", "Nombre": "DWS Floating Rate", "Cant": 714.627, "Coste": 63822.16, "P_Act": 92.86, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2024-11-26", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 45.7244, "Coste": 7000.00, "P_Act": 160.22, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2024-11-27", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "FI0008811997", "Nombre": "Evli Nordic Corp", "Cant": 19.6043, "Coste": 3000.00, "P_Act": 160.22, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2025-02-05", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 203.1068, "Coste": 5000.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR", "Ult_Act": f_init},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR", "Ult_Act": f_init}
        ]

    def cargar_diario_operaciones():
        return [
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "Compra inicial", "Importe": 63822.16, "Detalle": "Entrada fondo monetario"},
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "Beneficio Traspasado", "Importe": 2230.00, "Detalle": "Plusvalía histórica consolidada"},
            {"Fecha": "2024-11-26", "Producto": "Evli Nordic Corp", "Operación": "Compra inicial", "Importe": 7000.00, "Detalle": "Entrada deuda nórdica"},
            {"Fecha": "2024-11-27", "Producto": "Evli Nordic Corp", "Operación": "Ampliación", "Importe": 3000.00, "Detalle": "Incremento posición"},
            {"Fecha": "2025-02-05", "Producto": "Numantia Patrimonio", "Operación": "Compra inicial", "Importe": 5000.00, "Detalle": "Entrada fondo"},
            {"Fecha": "2025-02-19", "Producto": "MSCI World Index", "Operación": "Compra inicial", "Importe": 5016.20, "Detalle": "Entrada MSCI World"},
            {"Fecha": "2025-03-04", "Producto": "Numantia Patrimonio", "Operación": "Ampliación", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-03-04", "Producto": "MSCI World Index", "Operación": "Ampliación", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-04-10", "Producto": "Numantia Patrimonio", "Operación": "Ampliación", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-05-01", "Producto": "MSCI World Index", "Operación": "Ampliación", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-08-13", "Producto": "MSCI World Index", "Operación": "Ampliación", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-09-02", "Producto": "UnitedHealth", "Operación": "Compra", "Importe": 1867.84, "Detalle": "Compra 7 acciones"},
            {"Fecha": "2025-09-02", "Producto": "Numantia Patrimonio", "Operación": "Ampliación", "Importe": 1000.00, "Detalle": "Incremento capital"},
            {"Fecha": "2025-09-16", "Producto": "JD.com", "Operación": "Compra", "Importe": 1710.79, "Detalle": "Compra 58 acciones"},
            {"Fecha": "2025-09-22", "Producto": "N. Exp. Textil", "Operación": "Compra inicial", "Importe": 1043.75, "Detalle": "Compra 1580 acciones"},
            {"Fecha": "2025-09-30", "Producto": "Numantia Patrimonio", "Operación": "Ampliación", "Importe": 451.82, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-10-09", "Producto": "N. Exp. Textil", "Operación": "Ampliación", "Importe": 1018.05, "Detalle": "Compra 1290 acciones"},
            {"Fecha": "2025-11-05", "Producto": "Pictet China Index", "Operación": "Compra inicial", "Importe": 999.98, "Detalle": "Entrada sector China"},
            {"Fecha": "2025-11-15", "Producto": "Numantia Patrimonio", "Operación": "Ampliación", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2026-01-05", "Producto": "Amper", "Operación": "Compra", "Importe": 2023.79, "Detalle": "Compra 10400 acciones"}
        ]

    def cargar_datos_aportaciones():
        return [
            {"Titular": "Ander", "Broker": "R4", "Fecha": date(2024, 8, 30), "Importe": 44000.0},
            {"Titular": "Ander", "Broker": "R4", "Fecha": date(2024, 9, 3), "Importe": 3000.0},
            {"Titular": "Xabat", "Broker": "R4", "Fecha": date(2024, 8, 30), "Importe": 30000.0},
        ]

    # --- 6. GESTIÓN DE ARCHIVOS ---
    ARCHIVO_CSV = "cartera_final_aguirre_uranga.csv"
    ARCHIVO_AP = "aportaciones_familiares.csv"

    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    if 'df_aportaciones' not in st.session_state:
        try:
            temp_ap = pd.read_csv(ARCHIVO_AP)
            temp_ap['Fecha'] = pd.to_datetime(temp_ap['Fecha']).dt.date
            st.session_state.df_aportaciones = temp_ap
        except:
            st.session_state.df_aportaciones = pd.DataFrame(cargar_datos_aportaciones())
            st.session_state.df_aportaciones.to_csv(ARCHIVO_AP, index=False)

    # --- 7. BARRA LATERAL (SOLO PARA ACCIONES) ---
    with st.sidebar:
        st.markdown("### 🏦 Administración")
        if st.button("🔄 Sincronizar Acciones", use_container_width=True):
            try:
                rate_data = yf.Ticker("EURUSD=X").history(period="1d")
                rate = rate_data["Close"].iloc[-1] if not rate_data.empty else 1.09
                st.session_state.rate_aguirre = rate
                ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        t_data = yf.Ticker(row['Ticker']).history(period="1d")
                        if not t_data.empty:
                            p_raw = t_data["Close"].iloc[-1]
                            st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate if row['Moneda'] == "USD" else p_raw
                            st.session_state.df_cartera.at[i, 'Ult_Act'] = ahora
                
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.toast("Acciones actualizadas")
                st.rerun()
            except: st.error("Error al sincronizar.")
        
        if st.button("🚨 Reiniciar Datos", type="secondary", use_container_width=True):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.rerun()

    # --- 8. PROCESAMIENTO ---
    rt = getattr(st.session_state, 'rate_aguirre', 1.09)
    df_v = st.session_state.df_cartera.copy()
    df_v['Valor Mercado'] = df_v['P_Act'] * df_v['Cant']
    df_v['Beneficio'] = df_v['Valor Mercado'] - df_v['Coste']
    df_v['Rentabilidad %'] = (df_v['Beneficio'] / df_v['Coste'] * 100)

    # --- 9. DASHBOARD SUPERIOR ---
    st.title("🏦 Cartera Agirre & Uranga")
    
    inv_total = df_v['Coste'].sum()
    val_total = df_v['Valor Mercado'].sum()
    ben_total = val_total - inv_total
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Capital Invertido", f"{inv_total:,.2f} €")
    c2.metric("Valor de Mercado", f"{val_total:,.2f} €")
    c3.metric("Beneficio Latente", f"{ben_total:,.2f} €", f"{(ben_total/inv_total*100 if inv_total > 0 else 0):.2f}%")
    st.divider()

    # --- 10. SECCIÓN DE ACCIONES (LECTURA) ---
    st.subheader("📈 Acciones")
    sub_acc = df_v[df_v['Tipo'] == "Acción"].copy()
    res_acc = sub_acc.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Valor Mercado':'sum','P_Act':'first','Beneficio':'sum','Ult_Act':'max'}).reset_index()
    res_acc['Rentabilidad %'] = (res_acc['Beneficio'] / res_acc['Coste'] * 100)
    res_acc['Precio Actual'] = res_acc.apply(lambda x: fmt_dual(x['P_Act'], x['Moneda'], rt, 4), axis=1)
    res_acc['Beneficio (€/$)'] = res_acc.apply(lambda x: fmt_dual(x['Beneficio'], x['Moneda'], rt), axis=1)

    with st.container(border=True):
        st.dataframe(
            res_acc[['Broker', 'Nombre', 'Cant', 'Coste', 'Valor Mercado', 'Precio Actual', 'Beneficio (€/$)', 'Rentabilidad %', 'Ult_Act']]
            .rename(columns={'Cant':'Títulos','Coste':'Inversión','Valor Mercado':'Valor (€)','Ult_Act':'Última Val.'})
            .style.applymap(resaltar_beneficio, subset=['Beneficio (€/$)', 'Rentabilidad %'])
            .format({"Títulos":"{:.2f}","Inversión":"{:.2f} €","Valor (€)":"{:.2f} €","Rentabilidad %":"{:.2f}%"}),
            use_container_width=True, hide_index=True
        )

    # --- 11. SECCIÓN DE FONDOS (EDITABLE MANUALMENTE) ---
    st.subheader("📊 Fondos de Inversión")
    st.info("💡 Haz doble clic en 'Precio Actual' para actualizar el valor del fondo manualmente.")
    
    sub_fon = df_v[df_v['Tipo'] == "Fondo"].copy()
    res_fon = sub_fon.groupby(['Nombre', 'Broker']).agg({
        'Cant':'sum',
        'Coste':'sum',
        'P_Act':'first',
        'Ult_Act':'max'
    }).reset_index()

    # Preparamos el editor
    with st.container(border=True):
        edited_fon = st.data_editor(
            res_fon,
            column_config={
                "Nombre": st.column_config.Column(disabled=True),
                "Broker": st.column_config.Column(disabled=True),
                "Cant": st.column_config.NumberColumn("Participaciones", format="%.4f", disabled=True),
                "Coste": st.column_config.NumberColumn("Inversión (€)", format="%.2f €", disabled=True),
                "P_Act": st.column_config.NumberColumn("Precio Actual", format="%.4f", min_value=0, required=True),
                "Ult_Act": st.column_config.Column("Última Val.", disabled=True)
            },
            use_container_width=True,
            hide_index=True,
            key="fondos_editor"
        )

        # LÓGICA DE ACTUALIZACIÓN AL CAMBIAR UN VALOR
        if not edited_fon.equals(res_fon):
            ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
            for i, row in edited_fon.iterrows():
                # Si el precio ha cambiado para este fondo
                if row['P_Act'] != res_fon.iloc[i]['P_Act']:
                    nombre_fondo = row['Nombre']
                    nuevo_precio = row['P_Act']
                    # Actualizamos todas las filas de este fondo en el DF principal
                    st.session_state.df_cartera.loc[st.session_state.df_cartera['Nombre'] == nombre_fondo, 'P_Act'] = nuevo_precio
                    st.session_state.df_cartera.loc[st.session_state.df_cartera['Nombre'] == nombre_fondo, 'Ult_Act'] = ahora
            
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.rerun()

    # --- 12. OTROS ELEMENTOS (DIARIO, GRÁFICOS, ETC.) ---
    st.divider()
    st.subheader("📜 Diario de Operaciones")
    df_ops = pd.DataFrame(cargar_diario_operaciones()).sort_values(by='Fecha', ascending=False)
    with st.container(border=True):
        st.dataframe(df_ops.style.format({"Importe": "{:,.2f} €"}), use_container_width=True, hide_index=True)

    st.subheader("📊 Análisis de Cartera")
    tabs = st.tabs(["Distribución Global", "Por Activo"])
    with tabs[0]:
        fig = px.pie(df_v, values='Valor Mercado', names='Nombre', hole=0.5)
        st.plotly_chart(fig, use_container_width=True)
