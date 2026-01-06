import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Mi Cartera de Inversiones", layout="wide")

st.title("📈 Mi Gestor de Acciones Personal")

# 1. Función para cargar datos (usamos un CSV como base de datos simple)
def cargar_datos():
    try:
        return pd.read_csv("cartera.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Ticker", "Fecha", "Cantidad", "Precio Compra"])

# 2. Formulario para añadir nuevas acciones
with st.sidebar:
    st.header("Añadir Nueva Compra")
    ticker = st.text_input("Símbolo (ej: AAPL, TSLA, MSFT)").upper()
    fecha = st.date_input("Fecha de compra", datetime.now())
    cantidad = st.number_input("Cantidad de acciones", min_value=0.0, step=1.0)
    precio_compra = st.number_input("Precio de compra ($)", min_value=0.0)
    
    if st.button("Guardar Acción"):
        nueva_fila = pd.DataFrame([[ticker, fecha, cantidad, precio_compra]], 
                                 columns=["Ticker", "Fecha", "Cantidad", "Precio Compra"])
        df = cargar_datos()
        df = pd.concat([df, nueva_fila], ignore_index=True)
        df.to_csv("cartera.csv", index=False)
        st.success(f"¡{ticker} añadido!")

# 3. Mostrar y calcular cartera
df_cartera = cargar_datos()

if not df_cartera.empty:
    st.subheader("Tu Portafolio en Tiempo Real")
    
    precios_actuales = []
    beneficios = []
    
    # Obtener precios de internet
    for index, row in df_cartera.iterrows():
        try:
            accion = yf.Ticker(row['Ticker'])
            precio_hoy = accion.history(period="1d")['Close'].iloc[-1]
            precios_actuales.append(round(precio_hoy, 2))
            
            # Cálculo: (Precio Actual - Precio Compra) * Cantidad
            ganancia = (precio_hoy - row['Precio Compra']) * row['Cantidad']
            beneficios.append(round(ganancia, 2))
        except:
            precios_actuales.append(0)
            beneficios.append(0)

    df_cartera['Precio Actual'] = precios_actuales
    df_cartera['Beneficio/Pérdida ($)'] = beneficios

    # Aplicar colores (Verde si gana, Rojo si pierde)
    def color_beneficio(val):
        color = 'green' if val > 0 else 'red'
        return f'color: {color}'

    st.dataframe(df_cartera.style.applymap(color_beneficio, subset=['Beneficio/Pérdida ($)']))

    # 4. Resumen Total
    total_ganado = sum(beneficios)
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("Balance Total de la Cartera", f"${total_ganado:,.2f}", 
                delta=f"{total_ganado:,.2f}")
else:
    st.info("Aún no tienes acciones. Añade una en el menú de la izquierda.")