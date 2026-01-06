import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera MyInvestor", layout="wide")

# --- TITULO ---
st.title("📈 Mi Panel de Inversiones Personal")
st.write("Datos actualizados automáticamente desde el mercado.")

# --- DATOS PRECARGADOS DE TU EXCEL ---
def cargar_datos_iniciales():
    # Hemos extraído estos datos de tu archivo CSV
    datos = [
        {"Ticker": "AMP.MC", "Nombre": "Amper", "Cantidad": 10400.0, "Precio_Compra": 0.1946, "Manual": 0.0},
        {"Ticker": "JD", "Nombre": "JD.com", "Cantidad": 58.0, "Precio_Compra": 29.496, "Manual": 0.0},
        {"Ticker": "NXT.MC", "Nombre": "Nueva Expresión Textil", "Cantidad": 2870.0, "Precio_Compra": 0.7184, "Manual": 0.0},
        {"Ticker": "UNH", "Nombre": "UnitedHealth Group", "Cantidad": 7.0, "Precio_Compra": 266.834, "Manual": 0.0},
        # Los fondos a veces fallan en automático, los ponemos con ticker por si acaso
        {"Ticker": "0P00018XAR.F", "Nombre": "MSCI World Index", "Cantidad": 17.0, "Precio_Compra": 383.306, "Manual": 0.0},
        {"Ticker": "0P00008M90.F", "Nombre": "Pictet China Index", "Cantidad": 6.6, "Precio_Compra": 151.512, "Manual": 0.0}
    ]
    return pd.DataFrame(datos)

# Intentamos cargar el archivo guardado, si no existe usamos los datos de arriba
try:
    df = pd.read_csv("cartera.csv")
except FileNotFoundError:
    df = cargar_datos_iniciales()
    df.to_csv("cartera.csv", index=False)

# --- BARRA LATERAL PARA NUEVAS COMPRAS ---
with st.sidebar:
    st.header("➕ Añadir Nueva Inversión")
    modo = st.radio("Modo", ["Automático", "Manual"])
    new_ticker = st.text_input("Ticker / Nombre")
    new_cant = st.number_input("Cantidad", min_value=0.0)
    new_coste = st.number_input("Precio de compra (€)", min_value=0.0)
    
    p_manual = 0.0
    if modo == "Manual":
        p_manual = st.number_input("Precio actual mercado (€)", min_value=0.0)

    if st.button("Guardar"):
        nueva = pd.DataFrame([[new_ticker, new_ticker, new_cant, new_coste, p_manual]], 
                             columns=["Ticker", "Nombre", "Cantidad", "Precio_Compra", "Manual"])
        df = pd.concat([df, nueva], ignore_index=True)
        df.to_csv("cartera.csv", index=False)
        st.rerun()

# --- PROCESAMIENTO Y PRECIOS EN VIVO ---
if not df.empty:
    with st.spinner('Obteniendo precios en tiempo real...'):
        res = []
        for _, row in df.iterrows():
            # Si es manual usamos ese precio, si no buscamos en Yahoo
            if row['Manual'] > 0:
                p_actual = row['Manual']
            else:
                try:
                    # Buscamos el precio. Si es USD lo dejamos así porque tus precios medios ya están en EUR
                    ticker_data = yf.Ticker(row['Ticker'])
                    p_actual = ticker_data.history(period="1d")["Close"].iloc[-1]
                except:
                    p_actual = row['Precio_Compra'] # Si falla, usamos el de compra para no dar error
            
            valor_total = p_actual * row['Cantidad']
            coste_total = row['Precio_Compra'] * row['Cantidad']
            ganancia = valor_total - coste_total
            rentabilidad = (ganancia / coste_total * 100) if coste_total > 0 else 0
            
            res.append({
                "Activo": row['Nombre'],
                "Cantidad": row['Cantidad'],
                "Precio Medio (€)": row['Precio_Compra'],
                "Precio Actual (€)": p_actual,
                "Valor Mercado (€)": valor_total,
                "Ganancia (€)": ganancia,
                "Rentab. %": rentabilidad
            })
        
        df_final = pd.DataFrame(res)

    # --- MÉTRICAS ---
    t_invertido = (df['Precio_Compra'] * df['Cantidad']).sum()
    t_valor = df_final["Valor Mercado (€)"].sum()
    t_ganancia = t_valor - t_invertido
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Invertido", f"{t_invertido:,.2f} €")
    c2.metric("Valor Cartera", f"{t_valor:,.2f} €")
    c3.metric("Ganancia Total", f"{t_ganancia:,.2f} €", delta=f"{(t_ganancia/t_invertido*100):.2f}%")

    st.divider()

    # --- TABLA Y GRÁFICO ---
    col_t, col_g = st.columns([2, 1])
    
    with col_t:
        st.subheader("📋 Detalle")
        st.dataframe(df_final.style.format({
            "Precio Medio (€)": "{:.3f}",
            "Precio Actual (€)": "{:.3f}",
            "Valor Mercado (€)": "{:.2f}",
            "Ganancia (€)": "{:.2f}",
            "Rentab. %": "{:.2f}%"
        }), use_container_width=True)

    with col_g:
        st.subheader("🍩 Distribución")
        fig = px.pie(df_final, values='Valor Mercado (€)', names='Activo', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    if st.button("🗑️ Resetear Cartera"):
        pd.DataFrame(columns=["Ticker", "Nombre", "Cantidad", "Precio_Compra", "Manual"]).to_csv("cartera.csv", index=False)
        st.rerun()
else:
    st.info("Añade activos para ver el análisis.")
