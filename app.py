import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Mi Cartera MyInvestor", layout="wide")

st.title("📈 Mi Panel de Inversiones (Versión Segura)")

# Función con tus datos de MyInvestor
def datos_base():
    return [
        {"Ticker": "AMP.MC", "Nombre": "Amper", "Cantidad": 10400.0, "Precio_Compra": 0.1946},
        {"Ticker": "JD", "Nombre": "JD.com", "Cantidad": 58.0, "Precio_Compra": 29.496},
        {"Ticker": "NXT.MC", "Nombre": "Nueva Expresión Textil", "Cantidad": 2870.0, "Precio_Compra": 0.7184},
        {"Ticker": "UNH", "Nombre": "UnitedHealth Group", "Cantidad": 7.0, "Precio_Compra": 266.834},
        {"Ticker": "IWDA.AS", "Nombre": "Fondo MSCI World", "Cantidad": 17.0, "Precio_Compra": 383.306},
        {"Ticker": "6006.HK", "Nombre": "Fondo Pictet China", "Cantidad": 6.6, "Precio_Compra": 151.512}
    ]

# Cargamos los datos directamente del código para evitar errores de archivos
df = pd.DataFrame(datos_base())

if not df.empty:
    with st.spinner('Actualizando precios de mercado...'):
        resultados = []
        for _, row in df.iterrows():
            try:
                # Intentamos obtener el precio
                ticker = yf.Ticker(row['Ticker'])
                hist = ticker.history(period="1d")
                if not hist.empty:
                    p_act = hist["Close"].iloc[-1]
                else:
                    p_act = row['Precio_Compra'] # Si no hay datos, usamos precio compra
            except:
                p_act = row['Precio_Compra'] # Si hay error, usamos precio compra
            
            v_mercado = p_act * row['Cantidad']
            coste_total = row['Precio_Compra'] * row['Cantidad']
            ganancia = v_mercado - coste_total
            
            resultados.append({
                "Activo": row['Nombre'],
                "Cant.": row['Cantidad'],
                "Coste Medio": round(row['Precio_Compra'], 3),
                "Precio Act.": round(p_act, 3),
                "Valor Mercado": round(v_mercado, 2),
                "Ganancia (€)": round(ganancia, 2)
            })
        
        df_res = pd.DataFrame(resultados)

    # Métricas principales
    t_inv = (df['Precio_Compra'] * df['Cantidad']).sum()
    t_val = df_res["Valor Mercado"].sum()
    t_gan = t_val - t_inv

    c1, c2, c3 = st.columns(3)
    c1.metric("Inversión Total", f"{t_inv:,.2f} €")
    c2.metric("Valor Cartera", f"{t_val:,.2f} €")
    c3.metric("Balance Total", f"{t_gan:,.2f} €", delta=f"{(t_gan/t_inv*100):.2f}%" if t_inv > 0 else "0%")

    st.divider()
    
    # Tabla y Gráfico
    col_t, col_g = st.columns([2, 1])
    with col_t:
        st.dataframe(df_res, use_container_width=True)
    with col_g:
        fig = px.pie(df_res, values='Valor Mercado', names='Activo', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Cargando datos...")
