# Grupo_5_2024

# Para instalar dependencias ejecutar en la terminal:

pip install -r requirements.txt

# Configurar conexión con MySql
Crear un archivo que se llame .env en la raíz del proyecto(al mismo nivel que lo archivos .gitignore, readme y requeriments) y copiar y rellenar las siguientes variables de entorno con los datos de sus credenciales de mysql y el nombre de su bd:

DB_ENGINE=django.db.backends.mysql
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

# Realizar migraciones
Para crearlas:
python manage.py makemigrations

Para aplicarlas:
python manage.py migrate

# Correr el proyecto:
Ejecutar en la terminal (estando ubicado al mismo nivel que el archivo manage.py):
python manage.py runserver