import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera MyInvestor", layout="wide")

st.title("📈 Mi Panel de Inversiones Personal")

# 1. Función para cargar y procesar datos
def cargar_datos():
    try:
        df = pd.read_csv("cartera.csv")
        if df.empty:
            return pd.DataFrame(columns=["Ticker", "Cantidad", "Precio_Compra"])
        # Agrupamos por Ticker para manejar compras múltiples automáticamente
        df_resumen = df.groupby("Ticker").apply(
            lambda x: pd.Series({
                "Cantidad": x["Cantidad"].sum(),
                "Coste_Total": (x["Cantidad"] * x["Precio_Compra"]).sum()
            })
        ).reset_index()
        df_resumen["Precio_Medio"] = df_resumen["Coste_Total"] / df_resumen["Cantidad"]
        return df_resumen
    except FileNotFoundError:
        return pd.DataFrame(columns=["Ticker", "Cantidad", "Precio_Compra"])

# 2. Formulario lateral
with st.sidebar:
    st.header("➕ Nueva Operación")
    # Para Nueva Expresión Textil usar Ticker: NXT.MC
    ticker = st.text_input("Ticker (ej: NXT.MC, SAN.MC, AAPL)").upper()
    cant = st.number_input("Cantidad de títulos", min_value=0.0, step=1.0)
    precio = st.number_input("Precio de esta compra (€)", min_value=0.0)
    
    if st.button("Añadir a mi Cartera"):
        nueva_compra = pd.DataFrame([[ticker, cant, precio]], columns=["Ticker", "Cantidad", "Precio_Compra"])
        try:
            historico = pd.read_csv("cartera.csv")
            df_final = pd.concat([historico, nueva_compra], ignore_index=True)
        except FileNotFoundError:
            df_final = nueva_compra
        df_final.to_csv("cartera.csv", index=False)
        st.success(f"Añadida compra de {ticker}")
        st.rerun()

# 3. Mostrar resultados
df_cartera = cargar_datos()

if not df_cartera.empty:
    with st.spinner('Consultando precios actuales...'):
        precios_vivos = []
        for t in df_cartera["Ticker"]:
            try:
                # Obtenemos el precio más reciente
                val = yf.Ticker(t).history(period="1d")["Close"].iloc[-1]
                precios_vivos.append(round(val, 4))
            except:
                precios_vivos.append(0)
        
        df_cartera["Precio Mercado"] = precios_vivos
        df_cartera["Valor Actual"] = df_cartera["Precio Mercado"] * df_cartera["Cantidad"]
        df_cartera["Ganancia (€)"] = df_cartera["Valor Actual"] - df_cartera["Coste_Total"]
        df_cartera["Rentabilidad %"] = (df_cartera["Ganancia (€)"] / df_cartera["Coste_Total"]) * 100

    # MÉTRICAS TOTALES
    total_invertido = df_cartera["Coste_Total"].sum()
    valor_total = df_cartera["Valor Actual"].sum()
    beneficio_total = valor_total - total_invertido
    porcentaje_total = (beneficio_total / total_invertido) * 100 if total_invertido > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Invertido Total", f"{total_invertido:,.2f} €")
    col2.metric("Valor de Mercado", f"{valor_total:,.2f} €")
    col3.metric("Beneficio Neto", f"{beneficio_total:,.2f} €", delta=f"{porcentaje_total:.2f}%")

    st.divider()

    # TABLA Y GRÁFICO
    c_tabla, c_grafico = st.columns([2, 1])
    
    with c_tabla:
        st.subheader("📋 Mis Posiciones")
        # Mostramos la tabla formateada
        st.dataframe(df_cartera[["Ticker", "Cantidad", "Precio_Medio", "Precio Mercado", "Ganancia (€)", "Rentabilidad %"]].style.format({
            "Precio_Medio": "{:.3f}€",
            "Precio Mercado": "{:.3f}€",
            "Ganancia (€)": "{:.2f}€",
            "Rentabilidad %": "{:.2f}%"
        }), use_container_width=True)

    with c_grafico:
        st.subheader("🏠 Distribución")
        fig = px.pie(df_cartera, values='Valor Actual', names='Ticker', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    if st.button("🗑️ Vaciar Cartera (Cuidado)"):
        pd.DataFrame(columns=["Ticker", "Cantidad", "Precio_Compra"]).to_csv("cartera.csv", index=False)
        st.rerun()
else:
    st.info("La cartera está vacía. Añade tu primera compra en el menú lateral.")
