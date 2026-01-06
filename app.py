import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera Total", layout="wide")

st.title("🏦 Mi Gestor de Inversiones (MyInvestor & More)")

# Función para cargar datos
def cargar_datos():
    try:
        return pd.read_csv("cartera.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Ticker", "Tipo", "Cantidad", "Precio_Compra"])

df = cargar_datos()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("➕ Añadir Activo")
    tipo = st.selectbox("Categoría", ["Acción", "Fondo Indexado", "Monetario", "ETF"])
    ticker = st.text_input("Símbolo (ej: NXT.MC, VOO, IWDA.AS)").upper()
    cantidad = st.number_input("Cantidad total", min_value=0.0, step=0.1)
    precio_medio = st.number_input("Precio medio de compra (€)", min_value=0.0)
    
    if st.button("Guardar en Cartera"):
        nueva_fila = pd.DataFrame([[ticker, tipo, cantidad, precio_medio]], 
                                 columns=["Ticker", "Tipo", "Cantidad", "Precio_Compra"])
        df = pd.concat([df, nueva_fila], ignore_index=True)
        df.to_csv("cartera.csv", index=False)
        st.success(f"¡{ticker} actualizado!")
        st.rerun()

# --- CÁLCULOS ---
if not df.empty:
    # Agrupamos por Ticker por si has metido el mismo varias veces
    df_agrupado = df.groupby(['Ticker', 'Tipo']).agg({
        'Cantidad': 'sum',
        'Precio_Compra': 'mean' # Media de los precios introducidos
    }).reset_index()

    with st.spinner('Actualizando precios de mercado...'):
        precios_actuales = []
        for t in df_agrupado['Ticker']:
            try:
                # Usamos yfinance para el precio actual
                precio = yf.Ticker(t).history(period="1d")['Close'].iloc[-1]
                precios_actuales.append(precio)
            except:
                precios_actuales.append(0)
        
        df_agrupado['Precio Actual'] = precios_actuales
        df_agrupado['Valor Total'] = df_agrupado['Precio Actual'] * df_agrupado['Cantidad']
        df_agrupado['Ganancia Absoluta'] = (df_agrupado['Precio Actual'] - df_agrupado['Precio_Compra']) * df_agrupado['Cantidad']
        df_agrupado['Rentabilidad %'] = ((df_agrupado['Precio Actual'] / df_agrupado['Precio_Compra']) - 1) * 100

    # --- MÉTRICAS SUPERIORES ---
    total_invertido = (df_agrupado['Precio_Compra'] * df_agrupado['Cantidad']).sum()
    valor_total_cartera = df_agrupado['Valor Total'].sum()
    beneficio_total = valor_total_cartera - total_invertido
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Inversión Real", f"{total_invertido:,.2f} €")
    col2.metric("Valor Actual", f"{valor_total_cartera:,.2f} €")
    col3.metric("Beneficio Total", f"{beneficio_total:,.2f} €", delta=f"{(beneficio_total/total_invertido)*100:.2f}%")

    st.divider()

    # --- TABLA Y GRÁFICO ---
    fila_tabla, fila_grafico = st.columns([2, 1])

    with fila_tabla:
        st.subheader("📋 Detalle de tus activos")
        # Estilo para colores de rentabilidad
        st.dataframe(df_agrupado.style.format({
            "Precio Actual": "{:.3f}€",
            "Valor Total": "{:.2f}€",
            "Ganancia Absoluta": "{:.2f}€",
            "Rentabilidad %": "{:.2f}%"
        }), use_container_width=True)

    with fila_grafico:
        st.subheader("🍩 Distribución")
        fig = px.pie(df_agrupado, values='Valor Total', names='Ticker', hole=.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    if st.button("🗑️ Resetear Cartera"):
        pd.DataFrame(columns=["Ticker", "Tipo", "Cantidad", "Precio_Compra"]).to_csv("cartera.csv", index=False)
        st.rerun()
else:
    st.info("Introduce tus activos de MyInvestor para empezar.")
