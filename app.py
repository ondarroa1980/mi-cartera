import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Nuestra Cartera Familiar - v43", layout="wide")

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

    # --- 4. DIARIO DE OPERACIONES (21 MOVIMIENTOS HISTÓRICOS) ---
    def cargar_diario_operaciones():
        return [
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Acción": "Suscripción", "Importe": 63822.16, "Detalle": "Compra inicial fondo monetario"},
            {"Fecha": "2024-09-27", "Producto": "DWS Floating Rate", "Acción": "Traspaso Neto", "Importe": 2230.00, "Detalle": "Plusvalía consolidada histórica"},
            {"Fecha": "2024-11-26", "Producto": "Evli Nordic Corp", "Acción": "Suscripción", "Importe": 7000.00, "Detalle": "Entrada en deuda corporativa nórdica"},
            {"Fecha": "2024-11-27", "Producto": "Evli Nordic Corp", "Acción": "Suscripción", "Importe": 3000.00, "Detalle": "Ampliación posición Evli"},
            {"Fecha": "2024-11-27", "Producto": "JPM US Short Duration", "Acción": "Suscripción", "Importe": 9999.96, "Detalle": "Compra inicial fondo JPM"},
            {"Fecha": "2025-02-05", "Producto": "Numantia Patrimonio", "Acción": "Suscripción", "Importe": 5000.00, "Detalle": "Entrada fondo Numantia"},
            {"Fecha": "2025-02-19", "Producto": "MSCI World Index", "Acción": "Suscripción", "Importe": 5016.20, "Detalle": "Compra inicial Fidelity MSCI World"},
            {"Fecha": "2025-03-04", "Producto": "Numantia Patrimonio", "Acción": "Suscripción", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-03-04", "Producto": "MSCI World Index", "Acción": "Suscripción", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-04-10", "Producto": "Numantia Patrimonio", "Acción": "Suscripción", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-05-01", "Producto": "MSCI World Index", "Acción": "Suscripción", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-08-13", "Producto": "MSCI World Index", "Acción": "Suscripción", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-09-02", "Producto": "UnitedHealth", "Acción": "Compra", "Importe": 1867.84, "Detalle": "Inversión en sector salud (7 acciones)"},
            {"Fecha": "2025-09-02", "Producto": "Numantia Patrimonio", "Acción": "Suscripción", "Importe": 1000.00, "Detalle": "Ampliación posición"},
            {"Fecha": "2025-09-16", "Producto": "JD.com", "Acción": "Compra", "Importe": 1710.79, "Detalle": "Inversión en tech China (58 acciones)"},
            {"Fecha": "2025-09-22", "Producto": "N. Exp. Textil", "Acción": "Compra", "Importe": 1043.75, "Detalle": "Inversión inicial (1580 acciones)"},
            {"Fecha": "2025-09-30", "Producto": "Numantia Patrimonio", "Acción": "Suscripción", "Importe": 451.82, "Detalle": "Aportación periódica"},
            {"Fecha": "2025-10-09", "Producto": "N. Exp. Textil", "Acción": "Compra", "Importe": 1018.05, "Detalle": "Ampliación posición (1290 acciones)"},
            {"Fecha": "2025-11-05", "Producto": "Pictet China Index", "Acción": "Suscripción", "Importe": 999.98, "Detalle": "Inversión indexada China"},
            {"Fecha": "2025-11-15", "Producto": "Numantia Patrimonio", "Acción": "Suscripción", "Importe": 500.00, "Detalle": "Aportación periódica"},
            {"Fecha": "2026-01-05", "Producto": "Amper", "Acción": "Compra", "Importe": 2023.79, "Detalle": "Especulación small-cap (10400 acciones)"},
            {"Fecha": "2026-01-08", "Producto": "JPM US Short Duration", "Acción": "Venta Total", "Importe": -556.32, "Detalle": "Cierre posición. Capital recuperado: 9.443,64 €"}
        ]

    # Gestión persistencia
    ARCHIVO_CSV = "cartera_v43.csv"
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

    # --- 5. SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            try:
                rate = yf.Ticker("EURUSD=X").history(period="1d")["Close"].iloc[-1]
                st.session_state.rate_fmt = rate
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        p_raw = yf.Ticker(row['Ticker']).history(period="1d")["Close"].iloc[-1]
                        st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate if row['Moneda'] == "USD" else p_raw
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Fallo de conexión.")

    # --- 6. PROCESAMIENTO ---
    rt = getattr(st.session_state, 'rate_fmt', 1.09)
    df = st.session_state.df_cartera.copy()
    df['Valor_Actual'] = df['P_Act'] * df['Cant']
    df['Beneficio_EUR'] = df['Valor_Actual'] - df['Coste']
    df['Rentabilidad'] = (df['Beneficio_EUR'] / df['Coste'] * 100).fillna(0)

    # --- 7. INTERFAZ ---
    st.title("🏦 Panel de Control Patrimonial")
    
    c1, c2, c3 = st.columns(3)
    b_acc = df[df['Tipo'] == 'Acción']['Beneficio_EUR'].sum()
    b_fon = df[df['Tipo'] == 'Fondo']['Beneficio_EUR'].sum()
    b_tot = df['Beneficio_EUR'].sum()

    c1.metric("Beneficio Acciones", f"{b_acc:,.2f} € ({b_acc*rt:,.2f} $)")
    c2.metric("Beneficio Fondos", f"{b_fon:,.2f} €")
    c3.metric("Beneficio TOTAL VIVO", f"{b_tot:,.2f} € ({b_tot*rt:,.2f} $)")
    st.divider()

    def fmt_moneda(v, mon, d=2):
        if mon == "USD": return f"{v:,.{d}f} € ({v*rt:,.2f} $)"
        return f"{v:,.{d}f} €"

    def mostrar_seccion(titulo, filtro):
        st.header(f"💼 {titulo}")
        df_sub = df[df['Tipo'] == filtro].copy()
        
        # TABLA RESUMEN
        res = df_sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Valor_Actual':'sum','Beneficio_EUR':'sum', 'P_Act': 'first'}).reset_index()
        res['Rent. %'] = (res['Beneficio_EUR'] / res['Coste'] * 100)
        
        # Nombres Sencillos para las columnas
        res = res.rename(columns={
            'Cant': 'Cantidad / Part.',
            'Coste': 'Dinero Invertido',
            'Valor_Actual': 'Valor Mercado',
            'P_Act': 'Precio Actual',
            'Rent. %': 'Rentabilidad %'
        })
        
        res['Precio'] = res.apply(lambda r: fmt_moneda(r['Precio Actual'], r['Moneda'], 4), axis=1)
        res['Beneficio (EUR/USD)'] = res.apply(lambda r: fmt_moneda(r['Beneficio_EUR'], r['Moneda']), axis=1)
        
        st.subheader(f"📊 Situación Actual ({titulo})")
        
        if filtro == "Fondo":
            st.warning("💡 **MODO EDICIÓN:** Haz doble clic en la casilla **'Precio Actual'** para actualizar el valor oficial del banco.")
            cols_fondo = ['Broker', 'Nombre', 'Cantidad / Part.', 'Dinero Invertido', 'Valor Mercado', 'Precio Actual', 'Beneficio (EUR/USD)', 'Rentabilidad %']
            edited = st.data_editor(
                res[cols_fondo].style.applymap(resaltar_beneficio, subset=['Beneficio (EUR/USD)']).format({"Cantidad / Part.":"{:.2f}","Dinero Invertido":"{:.2f} €","Valor Mercado":"{:.2f} €","Rentabilidad %":"{:.2f}%"}),
                use_container_width=True,
                disabled=['Broker', 'Nombre', 'Cantidad / Part.', 'Dinero Invertido', 'Valor Mercado', 'Beneficio (EUR/USD)', 'Rentabilidad %'],
                key=f"ed_{filtro}"
            )
            for i, row in edited.iterrows():
                st.session_state.df_cartera.loc[st.session_state.df_cartera['Nombre'] == row['Nombre'], 'P_Act'] = row['Precio Actual']
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
        else:
            cols_accion = ['Broker', 'Nombre', 'Cantidad / Part.', 'Dinero Invertido', 'Valor Mercado', 'Precio', 'Beneficio (EUR/USD)', 'Rentabilidad %']
            st.dataframe(res[cols_accion].style.applymap(resaltar_beneficio, subset=['Beneficio (EUR/USD)']).format({"Cantidad / Part.":"{:.2f}","Dinero Invertido":"{:.2f} €","Valor Mercado":"{:.2f} €","Rentabilidad %":"{:.2f}%"}), use_container_width=True)

        # DESGLOSE
        st.subheader(f"📜 Detalle de Compras ({titulo})")
        for n in df_sub['Nombre'].unique():
            compras = df_sub[df_sub['Nombre'] == n].sort_values(by='Fecha', ascending=False).copy()
            compras['P_Fmt'] = compras.apply(lambda r: fmt_moneda(r['P_Act'], r['Moneda'], 4), axis=1)
            compras['B_Fmt'] = compras.apply(lambda r: fmt_moneda(r['Beneficio_EUR'], r['Moneda']), axis=1)
            with st.expander(f"Ver historial: {n}"):
                st.table(compras[['Fecha','Cant','Coste','P_Fmt','B_Fmt','Rentabilidad']].rename(columns={'Cant':'Cant','Coste':'Invertido','P_Fmt':'Precio','B_Fmt':'Beneficio','Rentabilidad':'Rent %'}).style.applymap(resaltar_beneficio, subset=['Beneficio']).format({"Cant":"{:.4f}","Invertido":"{:.2f} €","Rent %":"{:.2f}%"}))

    mostrar_seccion("Acciones", "Acción")
    st.divider()
    mostrar_seccion("Fondos de Inversión", "Fondo")

    # --- 8. DIARIO COMPLETO ---
    st.divider()
    st.header("📜 Diario Histórico de Operaciones")
    st.info("Rastro completo de vuestra evolución financiera (21 movimientos).")
    df_ops = pd.DataFrame(cargar_diario_operaciones()).sort_values(by='Fecha', ascending=False)
    st.dataframe(df_ops.style.applymap(lambda x: 'background-color: #f8d7da' if isinstance(x, (int, float)) and x < 0 else 'background-color: #d4edda' if isinstance(x, (int, float)) and x > 0 else None, subset=['Importe']).format({"Importe": "{:,.2f} €"}), use_container_width=True)

    st.divider()
    st.plotly_chart(px.pie(df, values='Valor_Actual', names='Nombre', title="Distribución de Activos Vivos", hole=0.4), use_container_width=True)
