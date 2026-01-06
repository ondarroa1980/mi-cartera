import streamlit as st
import pd as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera Consolidada", layout="wide")

# --- 1. DATOS REALES CALCULADOS (MYINVESTOR + RENTA 4) ---
def inicializar_datos_reales():
    return [
        # ACCIONES MYINVESTOR (De tu historial de compras)
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "AMP.MC", "Nombre": "Amper", "Cantidad": 10400.0, "Inversion": 2023.79, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "NXT.MC", "Nombre": "N. Exp. Textil", "Cantidad": 2870.0, "Inversion": 2061.80, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "UNH", "Nombre": "UnitedHealth", "Cantidad": 7.0, "Inversion": 1867.84, "Precio_Act": 0.0},
        {"Tipo": "Acción", "Broker": "MyInvestor", "Ticker": "JD", "Nombre": "JD.com", "Cantidad": 58.0, "Inversion": 1710.79, "Precio_Act": 0.0},
        
        # FONDOS MYINVESTOR
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "F-MSCI", "Nombre": "MSCI World Index", "Cantidad": 17.0, "Inversion": 6516.20, "Precio_Act": 383.30},
        {"Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "F-CHINA", "Nombre": "Pictet China Index", "Cantidad": 6.6, "Inversion": 999.98, "Precio_Act": 151.51},
        
        # FONDOS RENTA 4 (Calculados con tu nuevo archivo de plusvalías)
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "DWS-FR", "Nombre": "DWS Floating Rate", "Cantidad": 714.627, "Inversion": 63931.67, "Precio_Act": 92.86},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "EVLI-N", "Nombre": "Evli Nordic Corp.", "Cantidad": 65.3287, "Inversion": 10000.00, "Precio_Act": 160.22},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "JPM-US", "Nombre": "JPM US Short Duration", "Cantidad": 87.425, "Inversion": 9999.96, "Precio_Act": 108.026},
        {"Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "R4-NUM", "Nombre": "Numantia Patrimonio", "Cantidad": 329.434, "Inversion": 7951.82, "Precio_Act": 25.936}
    ]

# Carga de datos persistente
if 'df_cartera' not in st.session_state:
    try:
        st.session_state.df_cartera = pd.read_csv("cartera_total_final.csv")
    except:
        st.session_state.df_cartera = pd.DataFrame(inicializar_datos_reales())

# --- 2. BARRA LATERAL (AÑADIR) ---
with st.sidebar:
    st.header("➕ Añadir Inversión")
    with st.form("nuevo_form"):
        tipo_n = st.selectbox("Tipo", ["Acción", "Fondo"])
        broker_n = st.selectbox("Broker", ["MyInvestor", "Renta 4"])
        ticker_n = st.text_input("Ticker / ISIN").upper()
        nombre_n = st.text_input("Nombre")
        cant_n = st.number_input("Cantidad", min_value=0.0)
        inv_n = st.number_input("Inversión Total (€)", min_value=0.0)
        if st.form_submit_button("Guardar"):
            nueva = pd.DataFrame([{"Tipo": tipo_n, "Broker": broker_n, "Ticker": ticker_n, "Nombre": nombre_n, "Cantidad": cant_n, "Inversion": inv_n, "Precio_Act": 0.0}])
            st.session_state.df_cartera = pd.concat([st.session_state.df_cartera, nueva], ignore_index=True)
            st.session_state.df_cartera.to_csv("cartera_total_final.csv", index=False)
            st.rerun()

# --- 3. ACTUALIZACIÓN DE BOLSA ---
@st.cache_data(ttl=3600)
def sync_market(df):
    try: rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
    except: rate = 1.09
    for i, row in df.iterrows():
        if row['Tipo'] == "Acción":
            try:
                p = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                df.at[i, 'Precio_Act'] = p / rate if row['Ticker'] in ['UNH', 'JD'] else p
            except: pass
    return df

if st.button("🔄 Actualizar Precios Acciones (Bolsa)"):
    st.session_state.df_cartera = sync_market(st.session_state.df_cartera)
    st.session_state.df_cartera.to_csv("cartera_total_final.csv", index=False)

# --- 4. INTERFAZ: ACCIONES ---
st.title("🏦 Panel de Control Patrimonial")

st.header("📈 Mis Acciones (MyInvestor)")
df_acc = st.session_state.df_cartera[st.session_state.df_cartera['Tipo'] == "Acción"].copy()
df_acc['Valor_Mercado'] = df_acc['Precio_Act'] * df_acc['Cantidad']
df_acc['G/P'] = df_acc['Valor_Mercado'] - df_acc['Inversion']
df_acc['%'] = (df_acc['G/P'] / df_acc['Inversion'] * 100) if not df_acc.empty else 0

st.dataframe(df_acc[['Nombre', 'Cantidad', 'Inversion', 'Precio_Act', 'Valor_Mercado', 'G/P', '%']].style.format({
    "Inversion": "{:.2f}€", "Precio_Act": "{:.3f}€", "Valor_Mercado": "{:.2f}€", "G/P": "{:.2f}€", "%": "{:.2f}%"
}), use_container_width=True)

# --- 5. INTERFAZ: FONDOS ---
st.header("🧱 Mis Fondos (MyInvestor & Renta 4)")
st.info("💡 Haz doble clic en 'Precio_Act' para actualizar el valor de tus fondos.")
df_fon = st.session_state.df_cartera[st.session_state.df_cartera['Tipo'] == "Fondo"].copy()
df_fon['Valor_Mercado'] = df_fon['Precio_Act'] * df_fon['Cantidad']
df_fon['G/P'] = df_fon['Valor_Mercado'] - df_fon['Inversion']

edited_fon = st.data_editor(df_fon, column_order=("Broker", "Nombre", "Inversion", "Precio_Act", "Valor_Mercado", "G/P"), use_container_width=True)

if not edited_fon.equals(df_fon):
    st.session_state.df_cartera.update(edited_fon)
    st.session_state.df_cartera.to_csv("cartera_total_final.csv", index=False)
    st.rerun()

# --- 6. RESUMEN GLOBAL ---
st.divider()
t_inv = st.session_state.df_cartera['Inversion'].sum()
t_val = (st.session_state.df_cartera['Precio_Act'] * st.session_state.df_cartera['Cantidad']).sum()

c1, c2, c3 = st.columns(3)
c1.metric("Patrimonio Total", f"{t_val:,.2f} €")
c2.metric("Total Invertido", f"{t_inv:,.2f} €")
c3.metric("Beneficio Acumulado", f"{(t_val-t_inv):,.2f} €", delta=f"{((t_val/t_inv-1)*100):.2f}%")

st.plotly_chart(px.pie(st.session_state.df_cartera, values='Inversion', names='Broker', hole=0.5, title="Distribución por Entidad"), use_container_width=True)

if st.button("🚨 Resetear todo"):
    st.session_state.df_cartera = pd.DataFrame(inicializar_datos_reales())
    st.session_state.df_cartera.to_csv("cartera_total_final.csv", index=False)
    st.rerun()
