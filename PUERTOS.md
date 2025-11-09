# 🔌 Puertos Configurados - NexiTrade

## Puertos del Sistema

Para evitar conflictos con otros servicios, NexiTrade usa los siguientes puertos:

| Servicio    | Puerto Externo | Puerto Interno | URL de Acceso                |
|-------------|---------------|----------------|------------------------------|
| **Frontend**| 3001          | 3000           | http://localhost:3001        |
| **Backend** | 8080          | 8000           | http://localhost:8080        |
| **API Docs**| 8080          | 8000           | http://localhost:8080/docs   |
| **PostgreSQL** | 5433       | 5432           | localhost:5433               |
| **Redis**   | 6380          | 6379           | localhost:6380               |

## 🌐 URLs Principales

### Acceso Usuario
- **Dashboard**: http://localhost:3001
- **API Documentation**: http://localhost:8080/docs
- **API Redoc**: http://localhost:8080/redoc

### Endpoints API
- **Health Check**: http://localhost:8080/healthz
- **Readiness**: http://localhost:8080/readyz
- **Status**: http://localhost:8080/api/status
- **Metrics**: http://localhost:8080/api/metrics
- **Kill Switch**: http://localhost:8080/api/kill

## 🔧 Cambiar Puertos

Si necesitas cambiar los puertos, edita `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "TU_PUERTO:8000"  # Cambia TU_PUERTO
  
  frontend:
    ports:
      - "TU_PUERTO:3000"  # Cambia TU_PUERTO
```

Y actualiza `.env`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:TU_PUERTO_BACKEND
```

## ⚠️ Verificar Puertos Disponibles

Antes de iniciar, verifica que los puertos estén libres:

```bash
# Verificar puerto 3001
lsof -i :3001

# Verificar puerto 8080
lsof -i :8080

# Verificar puerto 5433
lsof -i :5433

# Verificar puerto 6380
lsof -i :6380
```

## 🛑 Liberar Puertos en Uso

Si algún puerto está ocupado:

```bash
# Matar proceso en puerto específico
lsof -ti:3001 | xargs kill -9
lsof -ti:8080 | xargs kill -9
```

O simplemente detén el servicio que los está usando.

## 🔒 Firewall

Si usas firewall, asegúrate de permitir estos puertos para localhost (127.0.0.1).

## 🐳 Puertos Internos de Docker

Dentro de la red Docker, los servicios se comunican por sus nombres y puertos internos:

- Backend ➜ Frontend: `http://backend:8000`
- Backend ➜ PostgreSQL: `postgres:5432`
- Backend ➜ Redis: `redis:6379`

**No necesitas cambiar estos**, solo los puertos externos que mapean a tu localhost.

