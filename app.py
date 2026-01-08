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

    # --- 4. DIARIO DE OPERACIONES ---
    def cargar_diario_operaciones():
        return [
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "Compra inicial", "Importe": 63822.16, "Detalle": "Entrada fondo monetario"},
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Operación": "Beneficio Traspasado", "Importe": 2230.00, "Detalle": "Plusvalía histórica consolidada"},
            {"Fecha": "2024-11-26", "Producto": "Evli Nordic Corp", "Operación": "Compra inicial", "Importe": 7000.00, "Detalle": "Entrada deuda nórdica"},
            {"Fecha": "2024-11-27", "Producto": "Evli Nordic Corp", "Operación": "Ampliación", "Importe": 3000.00, "Detalle": "Incremento posición"},
            {"Fecha": "2024-11-27", "Producto": "JPM US Short Duration", "Operación": "Compra inicial", "Importe": 9999.96, "Detalle": "Entrada posición"},
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
            {"Fecha": "2026-01-05", "Producto": "Amper", "Operación": "Compra", "Importe": 2023.79, "Detalle": "Compra 10400 acciones"},
            {"Fecha": "2026-01-08", "Producto": "JPM US Short Duration", "Operación": "VENTA TOTAL", "Importe": -556.32, "Detalle": "Cierre por estancamiento. Recuperado: 9.443,64 €"}
        ]

    # --- 5. GESTIÓN DE ARCHIVOS ---
    ARCHIVO_CSV = "cartera_final_ Aguirre_Uranga.csv"
    if 'df_cartera' not in st.session_state:
        try: st.session_state.df_cartera = pd.read_csv(ARCHIVO_CSV)
        except:
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)

    def resaltar_beneficio(val):
        if isinstance(val, str) and "€" in val:
            try:
                num = float(val.split("€")[0].replace(",", "").strip())
                if num > 0: return 'background-color: #d4edda'
                if num < 0: return 'background-color: #f8d7da'
            except: return None
        return None

    # --- 6. BARRA LATERAL (CON SINCRONIZACIÓN QUIRÚRGICA) ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            success_count = 0
            fail_tickers = []
            try:
                # Obtener tipo de cambio
                exchange_data = yf.Ticker("EURUSD=X").history(period="1d")
                rate = exchange_data["Close"].iloc[-1] if not exchange_data.empty else getattr(st.session_state, 'rate_aguirre', 1.09)
                st.session_state.rate_aguirre = rate
                
                # Sincronizar acciones una a una
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        try:
                            ticker_data = yf.Ticker(row['Ticker']).history(period="1d")
                            if not ticker_data.empty:
                                p_raw = ticker_data["Close"].iloc[-1]
                                st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate if row['Moneda'] == "USD" else p_raw
                                success_count += 1
                            else: fail_tickers.append(row['Ticker'])
                        except: fail_tickers.append(row['Ticker'])
                
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                if fail_tickers: st.warning(f"Actualizado con avisos en: {', '.join(set(fail_tickers))}")
                else: st.success(f"Sincronizado: {success_count} acciones.")
                st.rerun()
            except Exception as e: st.error(f"Error de red: {e}")
        
        if st.button("🚨 Reiniciar Datos"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            st.rerun()

    # --- 7. PROCESAMIENTO DE DATOS ---
    rt = getattr(st.session_state, 'rate_aguirre', 1.09)
    df = st.session_state.df_cartera.copy()
    df = df[df['Nombre'] != "JPM US Short Duration"] # Limpieza de cerrados
    
    df['Valor Mercado'] = df['P_Act'] * df['Cant']
    df['Beneficio (€)'] = df['Valor Mercado'] - df['Coste']
    df['Rentabilidad %'] = (df['Beneficio (€)'] / df['Coste'] * 100).fillna(0)

    # --- 8. INTERFAZ: MÉTRICAS GLOBALES ---
    st.title("🏦 Cartera Agirre & Uranga")
    
    # Cálculos globales
    total_invertido = df['Coste'].sum()
    total_mercado = df['Valor Mercado'].sum()
    total_beneficio = total_mercado - total_invertido
    rent_total = (total_beneficio / total_invertido * 100) if total_invertido > 0 else 0

    # Fila de métricas principales
    m1, m2, m3 = st.columns(3)
    m1.metric("Dinero Total Invertido", f"{total_invertido:,.2f} €")
    m2.metric("Valor Actual de Cartera", f"{total_mercado:,.2f} €")
    m3.metric("Beneficio TOTAL VIVO", f"{total_beneficio:,.2f} €", f"{rent_total:,.2f}%")
    
    st.divider()

    # Segunda fila de métricas (Por tipo)
    c1, c2 = st.columns(2)
    b_acc = df[df['Tipo'] == 'Acción']['Beneficio (€)'].sum()
    b_fon = df[df['Tipo'] == 'Fondo']['Beneficio (€)'].sum()
    c1.metric("Beneficio Acum. Acciones", f"{b_acc:,.2f} €")
    c2.metric("Beneficio Acum. Fondos", f"{b_fon:,.2f} €")
    
    st.divider()

    # --- 9. SECCIONES DETALLADAS ---
    def fmt_mon(v, mon, d=2):
        if mon == "USD": return f"{v:,.{d}f} € ({v*rt:,.2f} $)"
        return f"{v:,.{d}f} €"

    def mostrar_seccion(titulo, filtro):
        st.header(f"💼 {titulo}")
        df_sub = df[df['Tipo'] == filtro].copy()
        
        res = df_sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Valor Mercado':'sum','Beneficio (€)':'sum', 'P_Act': 'first'}).reset_index()
        res['Rentabilidad %'] = (res['Beneficio (€)'] / res['Coste'] * 100)
        res['Beneficio (EUR/USD)'] = res.apply(lambda r: fmt_mon(r['Beneficio (€)'], r['Moneda']), axis=1)
        res = res.rename(columns={'Cant': 'Cantidad / Part.', 'Coste': 'Dinero Invertido', 'P_Act': 'Precio Actual'})

        st.subheader(f"📊 Resumen {titulo}")
        
        if filtro == "Fondo":
            st.info("💡 Haz doble clic en 'Precio Actual' para actualizar el valor liquidativo.")
            cols_fon = ['Broker', 'Nombre', 'Cantidad / Part.', 'Dinero Invertido', 'Valor Mercado', 'Precio Actual', 'Beneficio (EUR/USD)', 'Rentabilidad %']
            edited = st.data_editor(
                res[cols_fon].style.applymap(resaltar_beneficio, subset=['Beneficio (EUR/USD)']).format({"Cantidad / Part.":"{:.4f}","Dinero Invertido":"{:.2f} €","Valor Mercado":"{:.2f} €","Rentabilidad %":"{:.2f}%"}),
                use_container_width=True,
                disabled=['Broker', 'Nombre', 'Cantidad / Part.', 'Dinero Invertido', 'Valor Mercado', 'Beneficio (EUR/USD)', 'Rentabilidad %'],
                key=f"ed_{filtro}"
            )
            for i, row in edited.iterrows():
                st.session_state.df_cartera.loc[st.session_state.df_cartera['Nombre'] == row['Nombre'], 'P_Act'] = row['Precio Actual']
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
        else:
            res['Precio'] = res.apply(lambda r: fmt_mon(r['Precio Actual'], r['Moneda'], 4), axis=1)
            cols_acc = ['Broker', 'Nombre', 'Cantidad / Part.', 'Dinero Invertido', 'Valor Mercado', 'Precio', 'Beneficio (EUR/USD)', 'Rentabilidad %']
            st.dataframe(res[cols_acc].style.applymap(resaltar_beneficio, subset=['Beneficio (EUR/USD)']).format({"Cantidad / Part.":"{:.2f}","Dinero Invertido":"{:.2f} €","Valor Mercado":"{:.2f} €","Rentabilidad %":"{:.2f}%"}), use_container_width=True)

        st.subheader(f"📜 Detalle de Compras ({titulo})")
        for n in df_sub['Nombre'].unique():
            com = df_sub[df_sub['Nombre'] == n].sort_values(by='Fecha', ascending=False).copy()
            com['P_Fmt'] = com.apply(lambda r: fmt_mon(r['P_Act'], r['Moneda'], 4), axis=1)
            com['B_Fmt'] = com.apply(lambda r: fmt_mon(r['Beneficio (€)'], r['Moneda']), axis=1)
            with st.expander(f"Ver historial: {n}"):
                st.table(com[['Fecha','Cant','Coste','P_Fmt','B_Fmt','Rentabilidad %']].rename(columns={'Cant':'Part.','Coste':'Invertido','P_Fmt':'Precio Actual','B_Fmt':'Beneficio'}).style.applymap(resaltar_beneficio, subset=['Beneficio']).format({"Part.":"{:.4f}","Invertido":"{:.2f} €","Rentabilidad %":"{:.2f}%"}))

    mostrar_seccion("Acciones", "Acción")
    st.divider()
    mostrar_seccion("Fondos de Inversión", "Fondo")

    # --- 10. DIARIO HISTÓRICO ---
    st.divider()
    st.header("📜 Diario Histórico de Operaciones")
    df_ops = pd.DataFrame(cargar_diario_operaciones()).sort_values(by='Fecha', ascending=False)
    st.dataframe(df_ops.style.applymap(lambda x: 'background-color: #f8d7da' if isinstance(x, (int, float)) and x < 0 else 'background-color: #d4edda' if isinstance(x, (int, float)) and x > 0 else None, subset=['Importe']).format({"Importe": "{:,.2f} €"}), use_container_width=True)

    # --- 11. GRÁFICA CIRCULAR ---
    st.divider()
    st.plotly_chart(px.pie(df, values='Valor Mercado', names='Nombre', title="Distribución de Activos Vivos", hole=0.4), use_container_width=True)
