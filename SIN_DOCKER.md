# 🚀 Ejecutar NexiTrade SIN Docker

Si no puedes o no quieres usar Docker, puedes ejecutar el proyecto localmente.

## ⚠️ Requisitos Previos

- **Python 3.11+**
- **Node.js 20+**
- **PostgreSQL 15+**
- **Redis** (opcional pero recomendado)

## 📦 Instalación

### 1. Instalar Python Dependencies

```bash
cd "app/backend"

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# o en Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Instalar PostgreSQL

**macOS (con Homebrew)**:
```bash
brew install postgresql@15
brew services start postgresql@15

# Crear base de datos
createdb nexitrade
```

**O usar PostgreSQL.app**:
- Descarga de: https://postgresapp.com/
- Inicia PostgreSQL.app
- Crea base de datos "nexitrade"

### 3. Instalar Redis (opcional)

```bash
brew install redis
brew services start redis
```

### 4. Configurar .env

```bash
cd "/Users/guti/Desktop/CURSOR WEBS/BOT CRYPTO"
cp .env.template .env
nano .env
```

Actualiza las URLs:
```bash
# En vez de postgres:5432, usa localhost:5432
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
```

### 5. Ejecutar Migraciones

```bash
cd app/backend
source venv/bin/activate
alembic upgrade head
```

### 6. Iniciar Backend

```bash
cd app/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

Backend disponible en: http://localhost:8080

### 7. Instalar Frontend Dependencies

```bash
cd app/frontend
npm install
```

### 8. Iniciar Frontend

```bash
cd app/frontend
npm run dev
```

Frontend disponible en: http://localhost:3001

---

## 🎯 Verificar que Funciona

1. **Backend Health Check**:
   ```bash
   curl http://localhost:8080/healthz
   ```

2. **Abrir Dashboard**:
   ```
   http://localhost:3001
   ```

---

## 🔧 Scripts de Ejecución

### Backend
```bash
cd app/backend
source venv/bin/activate

# Paper trading
python -m scripts.run_paper

# Backtest
python -m scripts.run_backtest

# Descargar datos
python -m scripts.seed_data
```

### Tests
```bash
cd app/backend
source venv/bin/activate
pytest tests/ -v
```

---

## 📝 Notas

- **PostgreSQL** debe estar corriendo antes de iniciar el backend
- **Redis** es opcional; sin él, algunas features de caché no funcionarán
- Para producción, se recomienda usar Docker por facilidad de deployment
- Abre **dos terminales**: una para backend, otra para frontend

---

## ⚙️ Troubleshooting

### "ModuleNotFoundError"
```bash
cd app/backend
source venv/bin/activate
pip install -r requirements.txt
```

### "Connection to database failed"
```bash
# Verificar PostgreSQL
psql -U nexi -d nexitrade -c "SELECT 1;"

# Si falla, crear usuario y BD
createuser -s nexi
createdb -O nexi nexitrade
```

### "Port already in use"
```bash
lsof -ti:8080 | xargs kill -9
lsof -ti:3001 | xargs kill -9
```

---

## 🐳 Ventajas de Docker vs Local

| Aspecto | Docker | Local |
|---------|--------|-------|
| Setup | Automático | Manual |
| Dependencies | Aisladas | Global |
| PostgreSQL | Incluido | Instalar aparte |
| Redis | Incluido | Instalar aparte |
| Portabilidad | Alta | Baja |
| Performance | ~5% overhead | Nativo |

**Recomendación**: Usa Docker si es posible. Es más fácil y reproducible.

