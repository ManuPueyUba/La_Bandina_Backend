# La Bandina Backend

Backend API para La Bandina - Simulador de Piano

## Tecnologías

- **FastAPI**: Framework web moderno para construir APIs
- **SQLAlchemy**: ORM para manejo de base de datos
- **PostgreSQL**: Base de datos principal
- **JWT**: Autenticación basada en tokens
- **Pydantic**: Validación de datos

## Características

- ✅ Autenticación de usuarios con JWT
- ✅ Gestión de usuarios
- ✅ Almacenamiento de composiciones
- ✅ Configuración de mapeo de teclas
- ✅ API RESTful
- ✅ Documentación automática con Swagger

## Instalación

### Con Docker (Recomendado)

1. Clona el repositorio
2. Asegúrate de tener Docker y Docker Compose instalados
3. Ejecuta el proyecto:

```bash
# Construir y ejecutar todo
docker-compose up --build

# O usar el Makefile (si tienes make instalado)
make build
make up
```

4. La API estará disponible en: http://localhost:8000
5. La documentación automática en: http://localhost:8000/docs

### Instalación Manual

1. Clona el repositorio
2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno:
```bash
cp .env.example .env
# Edita .env con tu configuración de base de datos
```

5. Crea las tablas de la base de datos:
```bash
python create_db.py
```

6. Ejecuta el servidor:
```bash
uvicorn main:app --reload
```

## Comandos Docker

```bash
# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down

# Limpiar todo (contenedores, imágenes, volúmenes)
docker-compose down -v && docker system prune -f

# Acceder al shell del contenedor
docker-compose exec api bash
```

## Endpoints

### Autenticación
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión

### Usuarios
- `GET /api/v1/users/me` - Obtener perfil actual
- `PUT /api/v1/users/me` - Actualizar perfil
- `GET /api/v1/users/{id}` - Obtener usuario por ID

### Composiciones
- `GET /api/v1/compositions/` - Listar composiciones
- `POST /api/v1/compositions/` - Crear composición
- `GET /api/v1/compositions/{id}` - Obtener composición
- `PUT /api/v1/compositions/{id}` - Actualizar composición
- `DELETE /api/v1/compositions/{id}` - Eliminar composición

### Mapeo de Teclas
- `GET /api/v1/keymaps/` - Listar configuraciones
- `POST /api/v1/keymaps/` - Crear configuración
- `GET /api/v1/keymaps/{id}` - Obtener configuración
- `PUT /api/v1/keymaps/{id}` - Actualizar configuración
- `DELETE /api/v1/keymaps/{id}` - Eliminar configuración

## Documentación

Una vez ejecutando el servidor, visita:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estructura del Proyecto

```
la_bandina_backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── compositions.py
│   │   │   └── keymaps.py
│   │   └── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── deps.py
│   ├── models/
│   │   ├── user.py
│   │   ├── composition.py
│   │   └── key_mapping.py
│   ├── schemas/
│   │   ├── auth.py
│   │   └── user.py
│   └── services/
│       ├── auth.py
│       └── user.py
├── main.py
├── create_db.py
├── requirements.txt
└── .env.example
```
