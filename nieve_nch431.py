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

st.subheader("Determinación de Cargas de Nieve según Norma NCh 431-2010")
st.caption("Análisis de Sobrecarga de Nieve en Cubiertas | Ingeniería Civil Estructural")

# =================================================================
# 2. SIDEBAR: PARÁMETROS TÉCNICOS (NCh 431)
# =================================================================
st.sidebar.header("⚙️ Parámetros de Diseño")

with st.sidebar.expander("📍 Ubicación Geográfica", expanded=True):
    latitud = st.selectbox("Latitud Sur", 
        ["17°-26°", "26°-29°", "29°-32°", "32°-34°", "34°-36°", "36°-38°", "38°-42°", "42°-48°", "48°-55°"], index=3)
    altitud = st.number_input("Altitud del lugar (m.s.n.m.)", value=500, step=100)

with st.sidebar.expander("🏗️ Propiedades del Techo", expanded=True):
    pendiente = st.slider("Pendiente del Techo (°)", 0, 70, 5)
    tipo_superficie = st.radio("Tipo de Superficie", ["Lisa (Vidrio/Metal/Membrana)", "Otras (Teja/Madera/Asfalto)"])

with st.sidebar.expander("🧪 Factores Normativos", expanded=True):
    # Categoría de Riesgo - Tabla 3 [cite: 163]
    cat_riesgo = st.selectbox("Categoría de Riesgo (Factor I)", ["I (0.8)", "II (1.0)", "III (1.1)", "IV (1.2)"], index=1)
    # Factor de Exposición - Tabla 4 [cite: 165]
    exposicion = st.selectbox("Exposición de Techos", ["Totalmente Expuesto", "Parcialmente Expuesto", "Protegido"], index=1)
    # Factor Térmico - Tabla 2 [cite: 159]
    cond_termica = st.selectbox("Condición Térmica (Ct)", ["Calefaccionado (1.0)", "Frío/Ventilado (1.1)", "Bajo Congelación (1.2)"], index=0)

# =================================================================
# 3. MOTOR DE CÁLCULO (LÓGICA NCh 431-2010)
# =================================================================

# Carga básica pg según Tabla 1 (Valores representativos del PDF) [cite: 134, 142]
def determinar_pg(lat, alt):
    if alt <= 300: return 0.25
    elif 300 < alt <= 600: return 0.25
    elif 600 < alt <= 1000: return 0.50
    elif 1000 < alt <= 1500: return 1.50
    elif 1500 < alt <= 2000: return 4.00
    else: return 6.00 # Valores de alta cordillera

pg = determinar_pg(latitud, altitud)
I_fact = float(cat_riesgo.split("(")[1][:-1]) # [cite: 163]
Ct_fact = float(cond_termica.split("(")[1][:-1]) # [cite: 159]

# Factor Ce según Categoría C y exposición - Tabla 4 [cite: 165]
ce_map = {"Totalmente Expuesto": 0.9, "Parcialmente Expuesto": 1.0, "Protegido": 1.1}
Ce_fact = ce_map[exposicion]

# Cálculo pf (Techo plano) - Ecuación 1 [cite: 147]
pf = 0.7 * Ce_fact * Ct_fact * I_fact * pg

# Factor de pendiente Cs - Figura 1 [cite: 212, 272]
def calcular_cs(ang, surf, ct):
    # Lógica de superficies lisas vs rugosas según Ct 
    lim_inf = 30 if surf == "Otras (Teja/Madera/Asfalto)" else (15 if ct >= 1.1 else 5)
    if ang <= lim_inf: return 1.0
    if ang >= 70: return 0.0
    return max(0, 1.0 - (ang - lim_inf) / (70 - lim_inf))

Cs = calcular_cs(pendiente, tipo_superficie, Ct_fact)
ps = Cs * pf # Carga final sobre techo inclinado [cite: 189]

# =================================================================
# 4. GENERADOR DE PDF PROFESIONAL (AUTOMÁTICO)
# =================================================================
def generar_pdf_nieve():
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("Logo.png"): pdf.image("Logo.png", x=10, y=8, w=33)
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "Memoria de Calculo: Nieve NCh 431-2010", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10); pdf.cell(0, 7, "Proyectos Estructurales | Mauricio Riquelme", ln=True, align='C')
    pdf.ln(10)

    pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, " 1. PARAMETROS DE DISENO", ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Ubicacion: Lat {latitud}, Alt {altitud} m.s.n.m. | pg: {pg:.2f} kN/m2", ln=True)
    pdf.cell(0, 8, f" Factores: Ce={Ce_fact}, Ct={Ct_fact}, I={I_fact} | Pendiente: {pendiente} deg", ln=True)
    pdf.ln(5)

    pdf.cell(0, 10, " 2. RESULTADOS ESTRUCTURALES", ln=True, fill=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 12, f" SOBRECARGA DE NIEVE DE DISENO (ps): {ps:.2f} kN/m2", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f" Carga Base Techo Plano (pf): {pf:.2f} kN/m2 | Factor Pendiente (Cs): {Cs:.2f}", ln=True)
    
    pdf.set_y(-25); pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Documento generado por AccuraWall Port - Analisis bajo NCh 431-2010", align='C')
    return pdf.output()

# Botón de Descarga Persistente en Sidebar
st.sidebar.markdown("---")
try:
    pdf_bytes = generar_pdf_nieve()
    b64 = base64.b64encode(pdf_bytes).decode()
    st.sidebar.markdown(f"""
        <a class="main-btn" href="data:application/pdf;base64,{b64}" download="Memoria_Nieve_NCh431.pdf">
            📥 DESCARGAR MEMORIA PDF
        </a>
    """, unsafe_allow_html=True)
except Exception as e:
    st.sidebar.error(f"Error PDF: {e}")

# =================================================================
# 5. DESPLIEGUE DE RESULTADOS
# =================================================================
st.markdown(f"""
<div class="classification-box">
    <strong>📋 Ficha Técnica de Nieve (NCh 431):</strong><br>
    Carga Básica Terreno (pg): {pg:.2f} kN/m²<br>
    Carga de Techo Plano (pf): {pf:.2f} kN/m²<br>
    Factor de Pendiente (Cs): {Cs:.2f}<br>
    <span style="font-size: 1.5em; color: #003366;"><strong>Sobrecarga Final (ps): {ps:.2f} kN/m²</strong></span>
</div>
""", unsafe_allow_html=True)

# Gráfico de Sensibilidad Dinámico
st.subheader("📈 Sensibilidad: Carga ps vs Pendiente del Techo")
angulos_eje = np.linspace(0, 70, 71)
c_curva = [calcular_cs(a, tipo_superficie, Ct_fact) * pf for a in angulos_eje]

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(angulos_eje, c_curva, color='#003366', lw=2.5, label='Curva de Diseño ps')
ax.scatter([pendiente], [ps], color='red', s=100, label='Punto Actual', zorder=5)
ax.set_xlabel("Pendiente del Techo (°)"); ax.set_ylabel("Carga ps (kN/m²)")
ax.grid(True, alpha=0.3); ax.legend(); st.pyplot(fig)



st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Mauricio Riquelme | Proyectos Estructurales <br> <em>'Programming is understanding'</em></div>", unsafe_allow_html=True)