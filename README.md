# Plataforma de Capacitación en Ciberseguridad (CyberSec Platform)

Plataforma desarrollada como proyecto de semillero universitario para capacitar a pequeñas empresas en ciberseguridad, mediante módulos interactivos y evaluaciones adaptativas por niveles.

Incluye:
- Registro e inicio de sesión con autenticación JWT.
- Módulos de aprendizaje (video o texto).
- Seguimiento de progreso por usuario.
- Examen único con clasificación automática (básico, intermedio, avanzado).

⸻

## 🚀 Ejecución local

1️⃣ Clonar el repositorio:
```
git clone https://github.com/tu_usuario/cybersec_platform.git
cd cybersec_platform
```

2️⃣ Crear entorno virtual e instalar dependencias:
```
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3️⃣ Configurar el archivo .env:
```
DATABASE_URL=postgresql+psycopg2://usuario:password@host:puerto/nombre_bd
SECRET_KEY=changeme
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
4️⃣ Ejecutar con Docker:
```
docker compose up --build
```
Abrir en el navegador: http://localhost:8000/docs

⸻

University research project designed to train small businesses in cybersecurity best practices using modular learning and adaptive assessments.

Features:
- User registration & login (JWT-based).
- Learning modules (video or text).
- User progress tracking.
- Single adaptive exam (basic/intermediate/advanced).
⸻

## 🚀 Run locally
```
git clone https://github.com/your_user/cybersec_platform.git
cd cybersec_platform
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
docker compose up --build
```

Access API docs at: http://localhost:8000/docs
