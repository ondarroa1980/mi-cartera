import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Nuestra Cartera Familiar - v40", layout="wide")

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
    
    # --- 3. BASE DE DATOS MAESTRA (ACTIVOS VIVOS ÚNICAMENTE) ---
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

    # --- 4. DIARIO DE OPERACIONES (Ventas cerradas) ---
    def cargar_diario_operaciones():
        return [
            {"Fecha": "2026-01-08", "Producto": "JPM US Short Duration", "Accion": "Venta Total", "Invertido": 9999.96, "Recuperado": 9443.64, "Resultado": -556.32, "Comentario": "Reasignación de capital"}
        ]

    # Gestión de persistencia
    ARCHIVO_CSV = "cartera_v40.csv"
    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    def resaltar_gp(val):
        if isinstance(val, str) and "€" in val:
            try:
                num = float(val.split("€")[0].replace(",", "").strip())
                if num > 0: return 'background-color: #d4edda'
                if num < 0: return 'background-color: #f8d7da'
            except: return None
        return None

    # --- 5. SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            try:
                rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
                st.session_state.rate_sync = rate
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        p_raw = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                        st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate if row['Moneda'] == "USD" else p_raw
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Error al sincronizar.")
        
        if st.button("🚨 Reiniciar Datos"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.rerun()

    # --- 6. PROCESAMIENTO ---
    rate_val = getattr(st.session_state, 'rate_sync', 1.09)
    df = st.session_state.df_cartera.copy()
    df['Valor_Actual'] = df['P_Act'] * df['Cant']
    df['GP_EUR'] = df['Valor_Actual'] - df['Coste']
    df['Rent. %'] = (df['GP_EUR'] / df['Coste'] * 100).fillna(0)

    # --- 7. INTERFAZ ---
    st.title("🏦 Cuadro de Mando Patrimonial")
    
    c1, c2, c3 = st.columns(3)
    gp_acc = df[df['Tipo'] == 'Acción']['GP_EUR'].sum()
    gp_fon = df[df['Tipo'] == 'Fondo']['GP_EUR'].sum()
    gp_tot = df['GP_EUR'].sum()

    c1.metric("G/P Acciones", f"{gp_acc:,.2f} € ({gp_acc*rate_val:,.2f} $)")
    c2.metric("G/P Fondos", f"{gp_fon:,.2f} €")
    c3.metric("G/P TOTAL VIVO", f"{gp_tot:,.2f} € ({gp_tot*rate_val:,.2f} $)")
    st.divider()

    def fmt_bi(val_eur, moneda, dec=2):
        if moneda == "USD":
            return f"{val_eur:,.{dec}f} € ({val_eur*rate_val:,.2f} $)"
        return f"{val_eur:,.{dec}f} €"

    def mostrar_seccion(titulo, filtro):
        st.header(f"💼 {titulo}")
        df_sub = df[df['Tipo'] == filtro].copy()
        
        # TABLA RESUMEN (Agrupada)
        res = df_sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Valor_Actual':'sum','GP_EUR':'sum', 'P_Act': 'first'}).reset_index()
        res['Rent. %'] = (res['GP_EUR'] / res['Coste'] * 100)
        res['P_Act_Fmt'] = res.apply(lambda r: fmt_bi(r['P_Act'], r['Moneda'], 4), axis=1)
        res['Ganancia_Fmt'] = res.apply(lambda r: fmt_bi(r['GP_EUR'], r['Moneda']), axis=1)
        
        st.subheader(f"📊 Situación Actual ({titulo})")
        cols_final = ['Broker', 'Nombre', 'Cant', 'Coste', 'Valor_Actual', 'P_Act_Fmt', 'Ganancia_Fmt', 'Rent. %']
        
        if filtro == "Fondo":
            st.warning("💡 **MODO EDICIÓN:** Haz doble clic en 'P_Act_Fmt' para actualizar el precio del banco.")
            # Editor para fondos (mostrando P_Act para editar)
            edited = st.data_editor(
                res[['Broker', 'Nombre', 'Cant', 'Coste', 'Valor_Actual', 'P_Act', 'Ganancia_Fmt', 'Rent. %']].style.applymap(resaltar_gp, subset=['Ganancia_Fmt']).format({"Cant":"{:.2f}","Coste":"{:.2f} €","Valor_Actual":"{:.2f} €","Rent. %":"{:.2f}%"}),
                use_container_width=True,
                disabled=['Broker', 'Nombre', 'Cant', 'Coste', 'Valor_Actual', 'Ganancia_Fmt', 'Rent. %'],
                key=f"ed_{filtro}"
            )
            for i, row in edited.iterrows():
                st.session_state.df_cartera.loc[st.session_state.df_cartera['Nombre'] == row['Nombre'], 'P_Act'] = row['P_Act']
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
        else:
            st.dataframe(res[cols_final].style.applymap(resaltar_gp, subset=['Ganancia_Fmt']).format({"Cant":"{:.2f}","Coste":"{:.2f} €","Valor_Actual":"{:.2f} €","Rent. %":"{:.2f}%"}), use_container_width=True)

        # DESGLOSE HISTÓRICO (Recuperado)
        st.subheader(f"📜 Detalle de Compras ({titulo})")
        for nombre in df_sub['Nombre'].unique():
            compras = df_sub[df_sub['Nombre'] == nombre].sort_values(by='Fecha', ascending=False).copy()
            compras['P_Fmt'] = compras.apply(lambda r: fmt_bi(r['P_Act'], r['Moneda'], 4), axis=1)
            compras['G_Fmt'] = compras.apply(lambda r: fmt_bi(r['GP_EUR'], r['Moneda']), axis=1)
            with st.expander(f"Ver todas las compras de: {nombre}"):
                st.table(compras[['Fecha','Cant','Coste','P_Fmt','G_Fmt','Rent. %']].style.applymap(resaltar_gp, subset=['G_Fmt']).format({"Cant":"{:.4f}","Coste":"{:.2f} €","Rent. %":"{:.2f}%"}))

    mostrar_seccion("Acciones", "Acción")
    st.divider()
    mostrar_seccion("Fondos de Inversión", "Fondo")

    # --- 8. DIARIO DE OPERACIONES REALIZADAS ---
    st.divider()
    st.header("📜 Diario de Operaciones Realizadas")
    df_realizadas = pd.DataFrame(cargar_diario_operaciones())
    st.table(df_realizadas.style.applymap(lambda x: 'background-color: #f8d7da' if isinstance(x, (int, float)) and x < 0 else 'background-color: #d4edda' if isinstance(x, (int, float)) and x > 0 else None, subset=['Resultado']).format({"Invertido": "{:.2f} €", "Recuperado": "{:.2f} €", "Resultado": "{:.2f} €"}))

    st.divider()
    st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución de Activos Vivos", hole=0.4), use_container_width=True)
