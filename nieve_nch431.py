# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import base64
import os
import math
from fpdf import FPDF

# =================================================================
# 1. CONFIGURACIÓN CORPORATIVA Y ESTILO
# =================================================================
st.set_page_config(page_title="NCh 431-2010 | Cargas de Nieve", layout="wide")

st.markdown("""
    <style>
    .main > div { padding-left: 2rem; padding-right: 2rem; max-width: 100%; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; }
    .classification-box {
        background-color: #f1f8ff; padding: 20px; border: 1px solid #c8e1ff;
        border-radius: 5px; margin-bottom: 25px;
    }
    .main-btn {
        display: flex; align-items: center; justify-content: center;
        background-color: #003366; color: white !important; padding: 12px 10px;
        text-decoration: none !important; border-radius: 8px; font-weight: bold;
        width: 100%; border: none; font-size: 14px; transition: 0.3s;
    }
    .main-btn:hover { background-color: #004488; }
    </style>
    """, unsafe_allow_html=True)

# Encabezado Corporativo
if os.path.exists("Logo.png"):
    with open("Logo.png", "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{logo_b64}" width="380"></div>', unsafe_allow_html=True)

st.subheader("Determinación de Cargas de Nieve según NCh 431-2010")
st.caption("Análisis de Sobrecarga de Nieve en Cubiertas | Ingeniería Civil Estructural")

# =================================================================
# 2. SIDEBAR: PARÁMETROS TÉCNICOS (NCh 431 TABLA 1)
# =================================================================
st.sidebar.header("⚙️ Parámetros de Diseño")

with st.sidebar.expander("📍 Ubicación Geográfica", expanded=True):
    latitud = st.selectbox("Latitud Sur", 
        ["17°-26°", "26°-29°", "29°-32°", "32°-34°", "34°-36°", "36°-38°", "38°-42°", "42°-48°", "48°-55°"], index=3)
    altitud = st.number_input("Altitud del lugar (m.s.n.m.)", value=500, step=100)

with st.sidebar.expander("🏗️ Propiedades del Techo", expanded=True):
    pendiente = st.slider("Pendiente del Techo (°)", 0, 70, 5)
    tipo_superficie = st.radio("Tipo de Superficie", ["Lisa (Vidrio/Metal)", "Otras (Teja/Madera)"])
    es_ventilado = st.checkbox("Techo Ventilado", value=True)

with st.sidebar.expander("🧪 Factores Normativos", expanded=True):
    cat_riesgo = st.selectbox("Categoría de Riesgo (Factor I)", ["I (0.8)", "II (1.0)", "III (1.1)", "IV (1.2)"], index=1)
    exposicion = st.selectbox("Factor de Exposición (Ce)", ["Totalmente Expuesto", "Parcialmente Expuesto", "Protegido"], index=1)
    cond_termica = st.selectbox("Factor Térmico (Ct)", ["Calefaccionado (1.0)", "Frío/Ventilado (1.1)", "No calefaccionado (1.2)"], index=0)

# =================================================================
# 3. MOTOR DE CÁLCULO (LOGICA NCH 431)
# =================================================================

# Determinar pg (Carga básica) según Tabla 1 (Simplificado para el motor)
# En una versión real, aquí va la matriz completa de la Tabla 1 del PDF 
def obtener_pg(lat, alt):
    # Lógica simplificada basada en tendencias de la Tabla 1 
    if alt < 300: return 0.25
    if 300 <= alt < 1000: return 0.50
    if 1000 <= alt < 2000: return 1.50
    return 3.00

pg = obtener_pg(latitud, altitud)
I = float(cat_riesgo.split("(")[1][:-1])
Ce = 1.0 if exposicion == "Parcialmente Expuesto" else (0.9 if exposicion == "Totalmente Expuesto" else 1.2) # Tabla 4 [cite: 165]
Ct = float(cond_termica.split("(")[1][:-1]) # Tabla 2 [cite: 159]

# Carga en Techo Plano (pf) [cite: 147]
pf = 0.7 * Ce * Ct * I * pg

# Factor de Pendiente (Cs) - Basado en Figura 1 [cite: 199, 272]
def calcular_cs(ang, surf, term):
    if ang <= 30: return 1.0
    if ang >= 70: return 0.0
    # Interpolación lineal básica para el ejemplo
    return 1.0 - (ang - 30) / 40

Cs = calcular_cs(pendiente, tipo_superficie, Ct)
ps = Cs * pf # Carga en techo inclinado [cite: 189]

# =================================================================
# 4. GENERADOR DE PDF PROFESIONAL
# =================================================================
def generar_pdf_nieve():
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("Logo.png"): pdf.image("Logo.png", x=10, y=8, w=33)
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "Memoria de Calculo: Nieve NCh 431-2010", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10); pdf.cell(0, 7, "Proyectos Estructurales | Structural Lab", ln=True, align='C')
    pdf.ln(15)

    pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, " 1. PARAMETROS DE UBICACION Y GEOMETRIA", ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Latitud: {latitud} | Altitud: {altitud} m.s.n.m. | Pendiente: {pendiente} deg", ln=True)
    pdf.cell(0, 8, f" Carga Basica (pg): {pg:.2f} kN/m2 | Factor Importancia (I): {I}", ln=True)
    pdf.ln(5)

    pdf.cell(0, 10, " 2. RESULTADOS DE CARGA DE DISENO", ln=True, fill=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f" CARGA SOBRE CUBIERTA (ps): {ps:.2f} kN/m2", ln=True)
    
    pdf.set_y(-25); pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Memoria generada por AccuraWall Port - Mauricio Riquelme", align='C')
    return pdf.output()

# Botón de Descarga Persistente
st.sidebar.markdown("---")
try:
    pdf_bytes = generar_pdf_nieve()
    b64 = base64.b64encode(pdf_bytes).decode()
    btn_html = f'''
        <a class="main-btn" href="data:application/pdf;base64,{b64}" download="Memoria_Nieve_NCh431.pdf">
            📥 DESCARGAR MEMORIA PDF
        </a>
    '''
    st.sidebar.markdown(btn_html, unsafe_allow_html=True)
except Exception as e:
    st.sidebar.error(f"Error PDF: {e}")

# =================================================================
# 5. DESPLIEGUE DE RESULTADOS
# =================================================================
st.markdown(f"""
<div class="classification-box">
    <strong>📋 Ficha Técnica de Nieve:</strong><br>
    Carga Básica Terreno (pg): {pg:.2f} kN/m²<br>
    Carga en Techo Plano (pf): {pf:.2f} kN/m²<br>
    <span style="font-size: 1.5em; color: #003366;"><strong>Carga Final de Diseño (ps): {ps:.2f} kN/m²</strong></span>
</div>
""", unsafe_allow_html=True)

# Gráfico de Sensibilidad
st.subheader("📈 Sensibilidad: Carga ps vs Pendiente")
angulos = np.linspace(0, 70, 50)
c_sens = [calcular_cs(a, tipo_superficie, Ct) * pf for a in angulos]

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(angulos, c_sens, color='#003366', lw=2.5, label='Carga ps (kN/m²)')
ax.scatter([pendiente], [ps], color='red', zorder=10)
ax.set_xlabel("Pendiente del Techo (°)"); ax.set_ylabel("Carga (kN/m²)")
ax.grid(True, alpha=0.3); ax.legend(); st.pyplot(fig)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Mauricio Riquelme | Proyectos Estructurales <br> <em>'Programming is understanding'</em></div>", unsafe_allow_html=True)