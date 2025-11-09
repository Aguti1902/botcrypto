# 🔧 Guía de Solución de Problemas - NexiTrade

## 🚨 Diagnóstico Rápido

Ejecuta el script de diagnóstico:

```bash
chmod +x diagnostico.sh
./diagnostico.sh
```

Esto te dirá exactamente qué está fallando.

---

## ❌ Problemas Comunes y Soluciones

### 1. "No funciona" / "No arranca"

#### Paso 1: Verificar que Docker esté corriendo
```bash
docker ps
```

**Si ves error**: Docker Desktop no está corriendo
- **macOS**: Abre Docker Desktop desde Applications
- **Windows**: Inicia Docker Desktop desde el menú de inicio
- Espera a que el ícono de Docker deje de estar animado

#### Paso 2: Verificar que el archivo .env existe
```bash
ls -la .env
```

**Si no existe**:
```bash
cp .env.template .env
nano .env  # o usa tu editor favorito
```

Configura al menos:
- `BINANCE_API_KEY`
- `BINANCE_SECRET`
- `ADMIN_TOKEN`

#### Paso 3: Levantar el sistema y ver logs
```bash
docker-compose up --build
```

**Observa los logs** - te dirán exactamente qué falla.

---

### 2. Error: "Port already in use"

```bash
# Ver qué está usando el puerto
lsof -i :3001
lsof -i :8080

# Matar el proceso
lsof -ti:3001 | xargs kill -9
lsof -ti:8080 | xargs kill -9

# O detén otros servicios manualmente
```

---

### 3. Error al construir imágenes Docker

```bash
# Limpiar todo y empezar de cero
docker-compose down -v
docker system prune -af
docker volume prune -f

# Reconstruir
docker-compose up --build
```

---

### 4. Backend no inicia / Errores de Python

**Ver logs específicos del backend**:
```bash
docker-compose logs backend
```

**Errores comunes**:

#### "ModuleNotFoundError"
```bash
# Entrar al contenedor
docker-compose exec backend /bin/bash

# Verificar instalación de paquetes
pip list

# Reinstalar si es necesario
pip install -r requirements.txt
```

#### "Database connection failed"
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres

# Ver logs de PostgreSQL
docker-compose logs postgres

# Reiniciar solo PostgreSQL
docker-compose restart postgres
```

#### "Alembic migration error"
```bash
# Entrar al backend
docker-compose exec backend /bin/bash

# Resetear migraciones (SOLO EN DESARROLLO)
rm -rf alembic/versions/*.py
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

### 5. Frontend no carga / Página en blanco

**Ver logs del frontend**:
```bash
docker-compose logs frontend
```

**Errores comunes**:

#### "Cannot find module 'next'"
```bash
# Reconstruir frontend
docker-compose build --no-cache frontend
docker-compose up frontend
```

#### "Failed to fetch from API"
- Verifica que el backend esté corriendo: http://localhost:8080/healthz
- Revisa la consola del navegador (F12)
- Verifica que `.env` tenga: `NEXT_PUBLIC_API_URL=http://localhost:8080`

---

### 6. "Cannot connect to Binance"

**En los logs ves "API credentials not configured"**:

1. Verifica que `.env` tenga las claves correctas
2. No uses comillas alrededor de los valores
3. No dejes espacios: `BINANCE_API_KEY=abc123` (NO `BINANCE_API_KEY = abc123`)

**Para testear sin claves reales**:
1. Usa Binance Testnet: https://testnet.binance.vision/
2. Configura `BINANCE_TESTNET=true` en `.env`

---

### 7. Dashboard muestra "Loading..." infinito

```bash
# 1. Verificar backend
curl http://localhost:8080/healthz

# 2. Verificar API
curl http://localhost:8080/api/status

# 3. Ver logs del frontend
docker-compose logs frontend

# 4. Verificar en navegador
# Abre F12 (DevTools) → Console → busca errores
```

---

### 8. Base de datos no se crea

```bash
# Verificar que PostgreSQL esté sano
docker-compose exec postgres psql -U nexi -d nexitrade -c "\dt"

# Si falla, resetear DB (PIERDE TODOS LOS DATOS)
docker-compose down -v
docker-compose up -d postgres
sleep 5
docker-compose up -d backend
make migrate
```

---

## 🐛 Debugging Avanzado

### Ver logs en tiempo real de todos los servicios
```bash
docker-compose logs -f
```

### Ver logs de un servicio específico
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Entrar a un contenedor para inspeccionar
```bash
# Backend
docker-compose exec backend /bin/bash
ls -la
cat main.py
python -c "import sys; print(sys.version)"

# Frontend
docker-compose exec frontend /bin/sh
ls -la
cat package.json

# PostgreSQL
docker-compose exec postgres psql -U nexi -d nexitrade
\dt  # listar tablas
SELECT * FROM orders LIMIT 10;
\q
```

### Verificar conectividad entre contenedores
```bash
# Desde backend, hacer ping a postgres
docker-compose exec backend ping postgres

# Verificar variables de entorno
docker-compose exec backend env | grep POSTGRES
```

### Reinstalar dependencias
```bash
# Backend
docker-compose exec backend pip install -r requirements.txt --force-reinstall

# Frontend
docker-compose exec frontend npm install
```

---

## 🆘 Último Recurso: Reset Completo

```bash
# 1. Detener todo
docker-compose down -v

# 2. Limpiar Docker
docker system prune -af
docker volume prune -f

# 3. Eliminar node_modules y .next (opcional)
rm -rf app/frontend/node_modules
rm -rf app/frontend/.next

# 4. Verificar .env
cat .env

# 5. Reconstruir desde cero
docker-compose build --no-cache

# 6. Iniciar
docker-compose up
```

---

## 📞 Reportar un Bug

Si después de todo esto sigue sin funcionar, proporciona:

1. **Output del script de diagnóstico**:
   ```bash
   ./diagnostico.sh > diagnostico.txt
   ```

2. **Logs completos**:
   ```bash
   docker-compose logs > logs.txt
   ```

3. **Tu configuración** (SIN claves privadas):
   ```bash
   cat .env | grep -v "KEY\|SECRET\|TOKEN" > config.txt
   ```

4. **Sistema operativo**:
   ```bash
   uname -a
   docker --version
   docker-compose --version
   ```

---

## ✅ Verificación Final

Si todo funciona correctamente, deberías ver:

```bash
# Todos los contenedores corriendo
docker-compose ps

# Todos "Up" y "healthy"
# Backend responde
curl http://localhost:8080/healthz
# → {"status":"healthy","service":"nexitrade"}

# Frontend carga
curl -I http://localhost:3001
# → HTTP/1.1 200 OK

# Dashboard se ve bien
open http://localhost:3001
```

---

## 💡 Tips de Desarrollo

- **Logs en tiempo real**: `make logs`
- **Solo backend**: `docker-compose up backend postgres redis`
- **Solo frontend**: `docker-compose up frontend`
- **Reiniciar un servicio**: `docker-compose restart backend`
- **Ver uso de recursos**: `docker stats`

---

**¿Sigue sin funcionar?** Ejecuta `./diagnostico.sh` y comparte la salida para ayudarte mejor.

