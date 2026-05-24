# 🛒 Sistema de Predicción de Demanda - Supermercados Holi

Sistema inteligente de análisis predictivo basado en Big Data para la toma de decisiones comerciales en Supermercados Holi - Lima, 2025.

## 🎯 Descripción

Este proyecto aplica técnicas de Big Data y Machine Learning sobre los datos de ventas de Supermercados Holi para:
- Limpiar y transformar datos crudos (ETL)
- Identificar patrones de demanda por producto, categoría y sede
- Predecir la demanda futura mediante Prophet
- Generar reportes ejecutivos en PDF

## 🛠️ Tecnologías

- **Python 3.11**
- **Streamlit** - Interfaz web
- **Pandas + NumPy** - ETL y análisis
- **Plotly** - Visualizaciones interactivas
- **Prophet** - Modelo predictivo
- **ReportLab** - Reportes PDF

## 📁 Estructura
SistemaHoli_UA/
├── app.py                  # Dashboard principal
├── data/                   # Datasets
├── modules/                # Módulos del sistema
│   ├── etl.py              # Limpieza y transformación
│   ├── analisis.py         # Análisis ABC y rotación
│   ├── prediccion.py       # Modelo Prophet
│   └── reportes.py         # Generación PDF
└── requirements.txt        # Dependencias

## 🚀 Cómo ejecutar

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Ejecutar la aplicación
streamlit run app.py
```

## 👥 Equipo

- Quispe Cabrera, Rosa
- Fernandez Caceres, Dayssy
- Bada Ccapia, Meier
- Roman Lugo, Michael
- Bazán Mendoza, Alejandro

## 📚 Curso

Big Data - VIII Ciclo  
Escuela Profesional de Ingeniería de Sistemas  
Lima, Perú - 2026
