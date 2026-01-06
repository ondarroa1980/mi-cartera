import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera Total", layout="wide")

st.title("🏦 Mi Gestor de Inversiones Global")

# Función para cargar datos
def cargar_datos():
    try:
        df = pd.read_csv("cartera.csv")
        # Asegurarnos de que existe la columna 'Tipo'
        if 'Tipo' not in df.columns:
            df['Tipo'] = 'Acción'
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Ticker", "Tipo", "Cantidad", "Precio Compra"])

df = cargar_datos()

# --- BARRA LATERAL: AÑADIR ACTIVOS ---
with st.sidebar:
    st.header("➕ Añadir Inversión")
    tipo = st.selectbox("Tipo de activo", ["Acción", "Fondo Indexado", "Monetario", "ETF"])
    ticker = st.text_input("Símbolo / Ticker").upper()
    cantidad = st.number_input("Cantidad", min_value=0.0, step=0.1)
    precio_compra = st.number_input("Precio de compra", min_value=0.0)
    
    if st.button("Guardar"):
        nueva_fila = pd.DataFrame([[ticker, tipo, cantidad, precio_compra]], 
                                 columns=["Ticker", "Tipo", "Cantidad", "Precio Compra"])
        df = pd.concat([df, nueva_fila], ignore_index=True)
        df.to_csv("cartera.csv", index=False)
        st.success("¡Guardado!")
        st.rerun()

# --- CUERPO PRINCIPAL ---
if not df.empty:
    with st.spinner('Actualizando precios...'):
        precios_actuales = []
        nombres = []
        
        for t in df['Ticker']:
            try:
                accion = yf.Ticker(t)
                # Intentamos sacar el nombre real de la empresa/fondo
                nombres.append(accion.info.get('shortName', t))
                precios_actuales.append(accion.history(period="1d")['Close'].iloc[-1])
            except:
                nombres.append(t)
                precios_actuales.append(0)

        df['Nombre'] = nombres
        df['Precio Actual'] = precios_actuales
        df['Valor Total'] = df['Precio Actual'] * df['Cantidad']
        df['Ganancia'] = (df['Precio Actual'] - df['Precio Compra']) * df['Cantidad']

    # --- MÉTRICAS ---
    total_invertido = (df['Precio Compra'] * df['Cantidad']).sum()
    valor_actual = df['Valor Total'].sum()
    ganancia_total = valor_actual - total_invertido
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Inversión Total", f"{total_invertido:,.2f}€")
    c2.metric("Valor de Cartera", f"{valor_actual:,.2f}€")
    c3.metric("Ganancia/Pérdida", f"{ganancia_total:,.2f}€", delta=f"{ganancia_total:,.2f}€")

    # --- GRÁFICO CIRCULAR ---
    st.divider()
    col_tabla, col_grafico = st.columns([2, 1])
    
    with col_tabla:
        st.subheader("📋 Detalle de Posiciones")
        st.dataframe(df[['Ticker', 'Tipo', 'Cantidad', 'Precio Compra', 'Precio Actual', 'Ganancia']], use_container_width=True)

    with col_grafico:
        st.subheader("🏠 Distribución")
        fig = px.pie(df, values='Valor Total', names='Ticker', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    if st.button("🗑️ Borrar toda la cartera"):
        pd.DataFrame(columns=["Ticker", "Tipo", "Cantidad", "Precio Compra"]).to_csv("cartera.csv", index=False)
        st.rerun()
else:
    st.info("Tu cartera está vacía. Añade tu primera inversión en el menú de la izquierda.")
