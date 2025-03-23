# Tasks - Sistema de Gestión de Tareas

## 📋 Descripción
Tasks es una aplicación web desarrollada con Django que permite gestionar tareas.

Proyecto desarrollado como parte de la materia Ingeniería de Software 2.

## ✨ Características Principales
- Gestión de espacios de trabajo colaborativos
- Tableros Kanban personalizables
- Sistema de listas con límite WIP (Work In Progress)
- Tarjetas con asignación de usuarios y fechas de vencimiento
- Dashboard con métricas y visualización de datos
- Sistema de autenticación personalizado
- Interfaz responsive y amigable

## 🛠️ Tecnologías Utilizadas
- Python 3.x
- Django
- Bootstrap 5
- JavaScript
- HTML5 & CSS3
- SQLite3
- Chart.js para visualizaciones
- Font Awesome para iconos

## 📦 Instalación y Configuración

1. Clonar el repositorio:
  bash
  git clone https://github.com/EdgarD19/PROY-IS2.git

2. Crear y activar entorno virtual:
   python -m venv venv
   source venv/bin/activate
   # En Windows: venv\Scripts\activate
   
4. Instalar dependencias:
   pip install -r requirements.txt

5. Realizar migraciones:
    python manage.py makemigrations
   
    python manage.py migrate
   
6. Iniciar servidor de desarrollo:
   python manage.py runserver
   

