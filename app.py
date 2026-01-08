import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime, date
# --- NUEVA IMPORTACIÓN NECESARIA PARA EL PDF ---
from fpdf import FPDF

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
    
    # --- 3. FUNCIONES DE APOYO (ESTILOS, MONEDA Y PDF) ---
    def resaltar_beneficio(val):
        try:
            if isinstance(val, str):
                clean_val = val.split(' ')[0].replace(',', '')
                num = float(clean_val)
            elif isinstance(val, (int, float)):
                num = val
            else: return None
            if num > 0: return 'background-color: #d4edda'
            if num < 0: return 'background-color: #f8d7da'
        except: pass
        return None

    def fmt_dual(valor_eur, moneda, tasa, decimales=2):
        if moneda == "USD":
            valor_usd = valor_eur * tasa
            return f"{valor_eur:,.{decimales}f} € ({valor_usd:,.2f} $)"
        return f"{valor_eur:,.{decimales}f} €"

    # --- NUEVA FUNCIÓN PARA GENERAR EL PDF ---
    def generar_resumen_pdf(inv_total, val_total, ben_total, total_a, total_x):
        pdf = FPDF()
        pdf.add_page()
        # Usamos Helvetica que es estándar y acepta caracteres básicos
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, f"Resumen Cartera Agirre & Uranga", ln=True, align='C')
        pdf.set_font("Helvetica", '', 10)
        pdf.cell(0, 10, f"Fecha del informe: {date.today().strftime('%d/%m/%Y')}", ln=True, align='C')
        pdf.ln(20)

        pdf.set_font("Helvetica", 'B', 14)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 10, "  Estado Actual de la Cartera (Activos Vivos)", ln=True, fill=True)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", '', 12)
        pdf.cell(0, 10, f"Dinero Total Invertido:   {inv_total:,.2f} EUR", ln=True)
        pdf.cell(0, 10, f"Valor Actual de Mercado:  {val_total:,.2f} EUR", ln=True)
        
        pdf.set_font("Helvetica", 'B', 12)
        color_ben = (0, 150, 0) if ben_total > 0 else (200, 0, 0)
        pdf.set_text_color(*color_ben)
        pdf.cell(0, 10, f"Beneficio Total Acumulado: {ben_total:,.2f} EUR", ln=True)
        pdf.set_text_color(0, 0, 0) # Reset color
        pdf.ln(20)

        pdf.set_font("Helvetica", 'B', 14)
        pdf.set_fill_color(255, 255, 200)
        pdf.cell(0, 10, "  Resumen de Aportaciones", ln=True, fill=True)
        pdf.ln(5)
        pdf.set_font("Helvetica", '', 12)
        pdf.cell(0, 10, f"Total aportado por Ander: {total_a:,.2f} EUR", ln=True)
        pdf.cell(0, 10, f"Total aportado por Xabat: {total_x:,.2f} EUR", ln=True)
        pdf.ln(5)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 10, f"GRAN TOTAL APORTADO:      {(total_a + total_x):,.2f} EUR", ln=True)

        # Devuelve los bytes del PDF codificados en latin-1 para compatibilidad
        return pdf.output(dest='S').encode('latin-1', 'ignore')

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
        if st.button("🔄 Sincronizar Bolsa (Acciones)"):
            try:
                rate_data = yf.Ticker("EURUSD=X").history(period="1d")
                rate = rate_data["Close"].iloc[-1] if not rate_data.empty else 1.09
                st.session_state.rate_aguirre = rate
                for i, row in st.session_state.df_cartera.iterrows():
                    if row['Tipo'] == "Acción":
                        t_data = yf.Ticker(row['Ticker']).history(period="1d")
                        if not t_data.empty:
                            p_raw = t_data["Close"].iloc[-1]
                            st.session_state.df_cartera.at[i, 'P_Act'] = p_raw / rate if row['Moneda'] == "USD" else p_raw
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.rerun()
            except: st.error("Error al sincronizar acciones.")
        
        if st.button("🚨 Reiniciar Datos"):
            st.session_state.df_cartera = pd.DataFrame(cargar_datos_maestros())
            st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
            temp_ap = pd.DataFrame(cargar_datos_aportaciones())
            st.session_state.df_aportaciones = temp_ap
            st.session_state.df_aportaciones.to_csv(ARCHIVO_AP, index=False)
            st.rerun()

    # --- 7. PROCESAMIENTO ---
    rt = getattr(st.session_state, 'rate_aguirre', 1.09)
    df_v = st.session_state.df_cartera.copy()
    df_v = df_v[df_v['Nombre'] != "JPM US Short Duration"]
    df_v['Valor Mercado'] = df_v['P_Act'] * df_v['Cant']
    df_v['Beneficio'] = df_v['Valor Mercado'] - df_v['Coste']
    df_v['Rentabilidad %'] = (df_v['Beneficio'] / df_v['Coste'] * 100)

    # --- 8. DASHBOARD SUPERIOR ---
    st.title("🏦 Cartera Agirre & Uranga")
    inv_total = df_v['Coste'].sum()
    val_total = df_v['Valor Mercado'].sum()
    ben_total = val_total - inv_total
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Dinero Invertido (Vivos)", f"{inv_total:,.2f} €")
    c2.metric("Valor Actual Cartera", f"{val_total:,.2f} €")
    c3.metric("Beneficio TOTAL VIVO", f"{ben_total:,.2f} €", f"{(ben_total/inv_total*100 if inv_total > 0 else 0):.2f}%")
    st.divider()

    # --- 9. TABLAS DE POSICIONES ---
    def mostrar_seccion(tit, tipo_filtro):
        st.header(f"💼 {tit}")
        sub = df_v[df_v['Tipo'] == tipo_filtro].copy()
        
        res = sub.groupby(['Nombre', 'Broker', 'Moneda']).agg({'Cant':'sum','Coste':'sum','Valor Mercado':'sum','P_Act':'first', 'Beneficio':'sum'}).reset_index()
        res['Rentabilidad %'] = (res['Beneficio'] / res['Coste'] * 100)
        
        res['Precio Actual'] = res['P_Act']
        res['Precio Visual'] = res.apply(lambda x: fmt_dual(x['P_Act'], x['Moneda'], rt, 4), axis=1)
        res['Beneficio (€/$)'] = res.apply(lambda x: fmt_dual(x['Beneficio'], x['Moneda'], rt), axis=1)
        
        res_display = res.rename(columns={'Cant': 'Cantidad / Part.', 'Coste': 'Inversión Total', 'Valor Mercado': 'Valor Actual (€)'})

        if tipo_filtro == "Fondo":
            st.info("💡 **MODO EDICIÓN:** Cambia el 'Precio Actual' y pulsa fuera de la celda. Luego dale al botón 'Guardar Precios de Fondos'.")
            columnas_fondo = ['Broker', 'Nombre', 'Cantidad / Part.', 'Inversión Total', 'Valor Actual (€)', 'Precio Actual', 'Beneficio (€/$)', 'Rentabilidad %']
            df_editado = st.data_editor(
                res_display[columnas_fondo].style.applymap(resaltar_beneficio, subset=['Beneficio (€/$)', 'Rentabilidad %'])
                .format({"Cantidad / Part.":"{:.4f}","Inversión Total":"{:.2f} €","Valor Actual (€)":"{:.2f} €","Rentabilidad %":"{:.2f}%", "Precio Actual":"{:.4f}"}),
                use_container_width=True,
                disabled=['Broker', 'Nombre', 'Cantidad / Part.', 'Inversión Total', 'Valor Actual (€)', 'Beneficio (€/$)', 'Rentabilidad %'],
                key="editor_fondos"
            )
            
            if st.button("💾 Guardar Precios de Fondos"):
                for index, row in df_editado.iterrows():
                    nombre_fondo = row['Nombre']
                    nuevo_precio = row['Precio Actual']
                    st.session_state.df_cartera.loc[st.session_state.df_cartera['Nombre'] == nombre_fondo, 'P_Act'] = nuevo_precio
                st.session_state.df_cartera.to_csv(ARCHIVO_CSV, index=False)
                st.success("Precios actualizados y cartera recalculada.")
                st.rerun()
        else:
            columnas_accion = ['Broker', 'Nombre', 'Cantidad / Part.', 'Inversión Total', 'Valor Actual (€)', 'Precio Visual', 'Beneficio (€/$)', 'Rentabilidad %']
            st.dataframe(
                res_display[columnas_accion].style.applymap(resaltar_beneficio, subset=['Beneficio (€/$)', 'Rentabilidad %'])
                .format({"Cantidad / Part.":"{:.4f}","Inversión Total":"{:.2f} €","Valor Actual (€)":"{:.2f} €","Rentabilidad %":"{:.2f}%"}),
                use_container_width=True
            )

        for n in sub['Nombre'].unique():
            with st.expander(f"Detalle de compras: {n}"):
                det = sub[sub['Nombre'] == n].copy()
                det['Precio Visual'] = det.apply(lambda x: fmt_dual(x['P_Act'], x['Moneda'], rt, 4), axis=1)
                det['Beneficio Visual'] = det.apply(lambda x: fmt_dual(x['Beneficio'], x['Moneda'], rt), axis=1)
                st.dataframe(
                    det[['Fecha', 'Cant', 'Coste', 'Precio Visual', 'Valor Mercado', 'Beneficio Visual', 'Rentabilidad %']]
                    .style.applymap(resaltar_beneficio, subset=['Rentabilidad %'])
                    .format({"Cant":"{:.4f}","Coste":"{:.2f} €","Valor Mercado":"{:.2f} €","Rentabilidad %":"{:.2f}%"}),
                    use_container_width=True, hide_index=True
                )

    mostrar_seccion("Acciones", "Acción")
    st.divider()
    mostrar_seccion("Fondos de Inversión", "Fondo")
    st.divider()

    # --- 10. DIARIO HISTÓRICO ---
    st.header("📜 Diario Histórico de Operaciones")
    df_ops = pd.DataFrame(cargar_diario_operaciones()).sort_values(by='Fecha', ascending=False)
    st.dataframe(df_ops.style.format({"Importe": "{:,.2f} €"}), use_container_width=True)
    st.divider()

    # --- 11. APORTACIONES FAMILIARES ---
    st.header("📑 Aportaciones Familiares (R4 + MyInvestor)")
    df_ap = st.session_state.df_aportaciones.copy()
    df_ap['Fecha'] = pd.to_datetime(df_ap['Fecha']).dt.date
    col_a, col_x = st.columns(2)
    with col_a:
        st.subheader("👨‍💼 ANDER")
        d_a = df_ap[df_ap['Titular'] == 'Ander'][['Broker', 'Fecha', 'Importe']].reset_index(drop=True)
        e_a = st.data_editor(d_a, num_rows="dynamic", key="ea", use_container_width=True)
        total_a = e_a['Importe'].sum()
        st.info(f"**TOTAL ANDER: {total_a:,.2f} €**")
    with col_x:
        st.subheader("👨‍💼 XABAT")
        d_x = df_ap[df_ap['Titular'] == 'Xabat'][['Broker', 'Fecha', 'Importe']].reset_index(drop=True)
        e_x = st.data_editor(d_x, num_rows="dynamic", key="ex", use_container_width=True)
        total_x = e_x['Importe'].sum()
        st.info(f"**TOTAL XABAT: {total_x:,.2f} €**")
    
    if st.button("💾 Guardar Aportaciones"):
        e_a['Titular'], e_x['Titular'] = 'Ander', 'Xabat'
        st.session_state.df_aportaciones = pd.concat([e_a, e_x])
        st.session_state.df_aportaciones.to_csv(ARCHIVO_AP, index=False)
        st.success("Aportaciones guardadas!")
        st.rerun()

    st.markdown(f"<div style='text-align: center; background: #ffeb3b; padding: 10px; border-radius: 10px; color: black; font-size: 20px; font-weight: bold;'>SUMA TOTAL APORTADO: {total_a + total_x:,.2f} €</div>", unsafe_allow_html=True)
    st.divider()

    # --- 12. GRÁFICAS (AL FINAL) ---
    st.header("📊 Análisis Visual de la Cartera")
    st.plotly_chart(px.pie(df_v, values='Valor Mercado', names='Nombre', title="Distribución Global", hole=0.4), use_container_width=True)
    g1, g2 = st.columns(2)
    with g1: st.plotly_chart(px.pie(df_v[df_v['Tipo']=='Acción'], values='Valor Mercado', names='Nombre', title="Pesos Acciones", hole=0.3), use_container_width=True)
    with g2: st.plotly_chart(px.pie(df_v[df_v['Tipo']=='Fondo'], values='Valor Mercado', names='Nombre', title="Pesos Fondos", hole=0.3), use_container_width=True)

    # --- 13. BOTÓN DE DESCARGA PDF (BARRA LATERAL) ---
    with st.sidebar:
        st.divider()
        st.header("🖨️ Informes")
        # Generamos el PDF en memoria usando los datos actuales
        pdf_bytes = generar_resumen_pdf(inv_total, val_total, ben_total, total_a, total_x)
        st.download_button(
            label="📄 Descargar Resumen PDF",
            data=pdf_bytes,
            file_name=f"Resumen_Cartera_{date.today()}.pdf",
            mime="application/pdf"
        )
