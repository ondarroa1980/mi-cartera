import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date

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
    
    # --- 3. FUNCIONES DE ESTILO Y FORMATEO ---
    def resaltar_beneficio(val):
        if isinstance(val, (int, float)):
            if val > 0: return 'background-color: #d4edda' # Verde para ganancias
            if val < 0: return 'background-color: #f8d7da' # Rojo para pérdidas
        return None

    def fmt_dual(valor_eur, moneda, tasa, decimales=2):
        """Formatea un valor para mostrar EUR y USD si corresponde."""
        if moneda == "USD":
            valor_usd = valor_eur * tasa
            return f"{valor_eur:,.{decimales}f} € ({valor_usd:,.2f} $)"
        return f"{valor_eur:,.{decimales}f} €"

    # --- 4. BASES DE DATOS ---
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
            {"Fecha": "2025-03-04", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 21.8300, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-04-10", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 25.2488, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-09-02", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 41.5863, "Coste": 1000.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-09-30", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 18.3846, "Coste": 451.82, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-11-15", "Tipo": "Fondo", "Broker": "Renta 4", "Ticker": "ES0173311103", "Nombre": "Numantia Patrimonio", "Cant": 19.2774, "Coste": 500.00, "P_Act": 25.9368, "Moneda": "EUR"},
            {"Fecha": "2025-02-19", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "IE00BYX5NX33", "Nombre": "MSCI World Index", "Cant": 549.942, "Coste": 6516.20, "P_Act": 12.6633, "Moneda": "EUR"},
            {"Fecha": "2025-11-05", "Tipo": "Fondo", "Broker": "MyInvestor", "Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cant": 6.6, "Coste": 999.98, "P_Act": 151.51, "Moneda": "EUR"}
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

    # --- 5. GESTIÓN DE ARCHIVOS ---
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
            temp_ap = pd.DataFrame(cargar_datos_aportaciones())
            st.session_state.df_aportaciones = temp_ap
            st.session_state.df_aportaciones.to_csv(ARCHIVO_AP, index=False)

    # --- 6. BARRA LATERAL ---
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🔄 Sincronizar Bolsa"):
            try:
                rate_data = yf.Ticker("EURUSD=X").history(period="1d")
                rate = rate_data["Close"].iloc[-1] if not rate_data.empty else 1.09
                st.session_state.rate_aguirre = rate
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        t_data = yf.Ticker(row['Ticker']).history(period="1d")
                        if not t_data.empty:
                            p_raw = t_data["Close"].iloc[-1]
                            # El precio de Yahoo siempre viene en la moneda del ticker. 
                            # Si es USD, lo convertimos a EUR dividiendo por la tasa.
                            st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate if row['Moneda'] == "USD" else p_raw
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Error al sincronizar.")
        
        if st.button("🚨 Reiniciar Datos"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            temp_ap = pd.DataFrame(cargar_datos_aportaciones())
            st.session_state.df_aportaciones = temp_ap
            st.session_state.df_aportaciones.to_csv(ARCHIVO_AP, index=False)
            st.rerun()

    # --- 7. PROCESAMIENTO ---
    rt = getattr(st.session_state, 'rate_aguirre', 1.085) # Tasa por defecto
    df_v = st.session_state.df_cartera.copy()
    df_v = df_v[df_v['Nombre'] != "JPM US Short Duration"]
    df_v['Val_Eur'] = df_v['P_Act'] * df_v['Cant']
    df_v['Ben_Eur'] = df_v['Val_Eur'] - df_v['Coste']
    df_v['Rent_Pct'] = (df_v['Ben_Eur'] / df_v['Coste'] * 100)

    # --- 8. DASHBOARD SUPERIOR ---
    st.title("🏦 Cartera Agirre & Uranga")
    
    t_inv = df_v['Coste'].sum()
    t_val = df_v['Val_Eur'].sum()
    t_ben = t_val - t_inv
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Dinero Invertido (Vivos)", f"{t_inv:,.2f} €")
    c2.metric("Valor Actual Cartera", f"{t_val:,.2f} €")
    c3.metric("Beneficio TOTAL VIVO", f"{t_ben:,.2f} €", f"{(t_ben/t_inv*100):.2f}%")
    st.divider()

    # --- 9. GRÁFICAS DE PESOS ---
    g1, g2 = st.columns(2)
    with g1: st.plotly_chart(px.pie(df_v[df_v['Tipo']=='Acción'], values='Val_Eur', names='Nombre', title="Pesos Acciones", hole=0.3), use_container_width=True)
    with g2: st.plotly_chart(px.pie(df_v[df_v['Tipo']=='Fondo'], values='Val_Eur', names='Nombre', title="Pesos Fondos", hole=0.3), use_container_width=True)
    st.divider()

    # --- 10. TABLAS DE ACTIVOS ---
    def mostrar_seccion(tit, tipo_filtro):
        st.header(f"💼 {tit}")
        sub = df_v[df_v['Tipo'] == tipo_filtro].copy()
        
        # Agregado para la tabla principal
        res = sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Val_Eur':'sum','P_Act':'first', 'Ben_Eur':'sum'}).reset_index()
        res['Rent_Pct'] = (res['Ben_Eur'] / res['Coste'] * 100)
        
        # Columnas de visualización dual
        res['Precio'] = res.apply(lambda x: fmt_dual(x['P_Act'], x['Moneda'], rt, 4), axis=1)
        res['Beneficio'] = res.apply(lambda x: fmt_dual(x['Ben_Eur'], x['Moneda'], rt), axis=1)
        
        # Formateo de tabla principal
        cols = ['Broker', 'Nombre', 'Cant', 'Coste', 'Val_Eur', 'Precio', 'Beneficio', 'Rent_Pct']
        st.dataframe(
            res[cols].style.applymap(resaltar_beneficio, subset=['Rent_Pct'])
            .format({"Cant":"{:.4f}","Coste":"{:.2f} €","Val_Eur":"{:.2f} €","Rent_Pct":"{:.2f}%"}),
            use_container_width=True
        )

        # Desglose de cada compra
        for n in sub['Nombre'].unique():
            with st.expander(f"Historial detallado: {n}"):
                compras = sub[sub['Nombre'] == n].copy()
                compras['Precio_Act'] = compras.apply(lambda x: fmt_dual(x['P_Act'], x['Moneda'], rt, 4), axis=1)
                compras['Ben_Visual'] = compras.apply(lambda x: fmt_dual(x['Ben_Eur'], x['Moneda'], rt), axis=1)
                
                det = compras[['Fecha', 'Cant', 'Coste', 'Precio_Act', 'Val_Eur', 'Ben_Eur', 'Ben_Visual', 'Rent_Pct']]
                st.dataframe(
                    det.style.applymap(resaltar_beneficio, subset=['Ben_Eur'])
                    .format({"Cant":"{:.4f}","Coste":"{:.2f} €","Val_Eur":"{:.2f} €","Rent_Pct":"{:.2f}%"}),
                    use_container_width=True,
                    hide_index=True
                )

    mostrar_seccion("Acciones", "Acción")
    st.divider()
    mostrar_seccion("Fondos de Inversión", "Fondo")
    st.divider()

    # --- 11. APORTACIONES FAMILIARES (AL FINAL) ---
    st.header("📑 Aportaciones Familiares (R4 + MyInvestor)")
    df_ap = st.session_state.df_aportaciones.copy()
    df_ap['Fecha'] = pd.to_datetime(df_ap['Fecha']).dt.date

    col_a, col_x = st.columns(2)
    with col_a:
        st.subheader("👨‍💼 ANDER")
        d_a = df_ap[df_ap['Titular'] == 'Ander'][['Broker', 'Fecha', 'Importe']].reset_index(drop=True)
        e_a = st.data_editor(d_a, num_rows="dynamic", key="ea", use_container_width=True,
                            column_config={"Importe": st.column_config.NumberColumn(format="%.2f €"),
                                           "Fecha": st.column_config.DateColumn()})
        total_a = e_a['Importe'].sum()
        st.info(f"**TOTAL ANDER: {total_a:,.2f} €**")

    with col_x:
        st.subheader("👨‍💼 XABAT")
        d_x = df_ap[df_ap['Titular'] == 'Xabat'][['Broker', 'Fecha', 'Importe']].reset_index(drop=True)
        e_x = st.data_editor(d_x, num_rows="dynamic", key="ex", use_container_width=True,
                            column_config={"Importe": st.column_config.NumberColumn(format="%.2f €"),
                                           "Fecha": st.column_config.DateColumn()})
        total_x = e_x['Importe'].sum()
        st.info(f"**TOTAL XABAT: {total_x:,.2f} €**")

    if st.button("💾 Guardar Aportaciones"):
        e_a['Titular'], e_x['Titular'] = 'Ander', 'Xabat'
        st.session_state.df_aportaciones = pd.concat([e_a, e_x])
        st.session_state.df_aportaciones.to_csv(ARCHIVO_AP, index=False)
        st.success("Aportaciones guardadas!")
        st.rerun()

    total_fam = total_a + total_x
    st.markdown(f"""
    <div style='text-align: center; background: #ffeb3b; padding: 15px; border-radius: 10px; color: black; font-size: 22px; font-weight: bold;'>
        SUMA TOTAL APORTADO: {total_fam:,.2f} €
    </div>
    """, unsafe_allow_html=True)
