# Grupo_5_2024

# Instalar dependencias:
Ejecutar en la terminal:

`pip install -r requirements.txt`


# Configurar conexión con MySql
Crear un archivo que se llame .env en la raíz del proyecto(al mismo nivel que lo archivos .gitignore, readme y requeriments) y copiar y rellenar las siguientes variables de entorno con los datos de sus credenciales de mysql y el nombre de su bd:

```
DB_ENGINE=django.db.backends.mysql
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
```


# Realizar migraciones de la base de datos hacia el proyecto
Este comando transforma las tablas de la base de datos en modelos de Django y los guarda en el archivo models.py:

`python manage.py inspectdb > app/models.py`


# Realizar migraciones desde el proyecto hacia la base de datos
Este comando crea un archivo de migración, de los modelos de Django que hayamos definido, en el archivo models.py:

`python manage.py makemigrations`

Este comando aplica los archivos de migracion pendientes a la base de datos:

`python manage.py migrate`


# Correr el proyecto:
Ejecutar en la terminal (estando ubicado al mismo nivel que el archivo manage.py):
`python manage.py runserver`


# Estructura del proyecto:

- **`app/`**: Carpeta con el codigo de la app, que contiene:
    - **`migrations/`**: Archivos para gestionar migraciones de base de datos.
    - **`static/`**: Archivos estáticos como CSS, JavaScript e imágenes.
    - **`templates/`**: Plantillas HTML utilizadas para renderizar las vistas de la aplicación.
    - **`templatetags/`**: Contiene funciones para aplicar en los templates.
    - **`models.py`**: Definición de modelos de datos.
    - **`urls.py`**: Define las rutas URL de la app.
    - **`views.py`**: Lógica de las vistas de la aplicación.

- **`finanzas/`**: 
  - Carpeta de conficuración del proyecto que contiene:
    - **`__init__.py`**: Indica que es un paquete Python.
    - **`settings.py`**: Configuraciones del proyecto (base de datos, aplicaciones, middleware).
    - **`urls.py`**: Define las rutas URL a nivel de proyecto.
    - **`wsgi.py`**: Punto de entrada para servidores WSGI.
    - **`asgi.py`**: Punto de entrada para servidores ASGI (opcional).