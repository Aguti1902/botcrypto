# 🚀 Guía de Inicio Rápido - NexiTrade

Esta guía te ayudará a poner en marcha NexiTrade en **menos de 10 minutos**.

## Paso 1: Preparar el Entorno (2 min)

### Requisitos
- Docker Desktop instalado ([Descargar](https://www.docker.com/products/docker-desktop))
- Cuenta de Binance (o usar testnet)

### Verificar Docker
```bash
docker --version
docker-compose --version
```

## Paso 2: Configurar Credenciales (3 min)

### 2.1 Copiar archivo de configuración
```bash
cd "BOT CRYPTO"
cp .env.template .env
```

### 2.2 Obtener API Keys de Binance

**Opción A: Testnet (Recomendado para empezar)**
1. Ir a [testnet.binance.vision](https://testnet.binance.vision/)
2. Generar API Key de testnet
3. Copiar API Key y Secret

**Opción B: Producción (Solo para usuarios avanzados)**
1. Login en [Binance.com](https://www.binance.com)
2. Account → API Management
3. Crear API Key
4. **Importante**: Deshabilitar "Enable Withdrawals"

### 2.3 Editar `.env`
```bash
# Abrir con tu editor favorito
nano .env
# o
code .env
```

Configurar al menos estas líneas:
```bash
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_SECRET=tu_secret_aqui
BINANCE_TESTNET=true

ADMIN_TOKEN=cambia_esto_por_un_token_largo_y_aleatorio
```

💡 **Tip**: Para generar un token seguro:
```bash
openssl rand -hex 32
```

## Paso 3: Levantar el Sistema (2 min)

```bash
# Construir e iniciar
make dev

# O si no tienes make:
docker-compose up --build
```

⏱️ Primera vez puede tomar 2-3 minutos descargando imágenes.

### Verificar que funciona
Deberías ver en los logs:
```
✅ Database initialized
✅ Binance initialized: TESTNET
🚀 Starting NexiTrade...
```

## Paso 4: Acceder al Dashboard (1 min)

Abre tu navegador:
- **Dashboard**: http://localhost:3001
- **API Docs**: http://localhost:8080/docs

## Paso 5: Primer Test - Paper Trading (2 min)

### 5.1 Verificar el estado
En el dashboard verás:
- Status: "running"
- Mode: "paper"
- Can Trade: "Yes"

### 5.2 Iniciar paper trading
En otra terminal:
```bash
make paper
```

### 5.3 Monitorear
- Ver logs: `make logs`
- Dashboard mostrará métricas en tiempo real

## 🎯 Próximos Pasos

### Opción 1: Ejecutar un Backtest
```bash
# Edita el periodo en app/backend/config/system.yaml
make backtest
```

### Opción 2: Ajustar Estrategias
Edita `app/backend/config/system.yaml`:
```yaml
strategies:
  trend_atr:
    enabled: true  # Cambiar a false para desactivar
    sma_fast: 50   # Ajustar parámetros
```

Reinicia:
```bash
make down
make dev
```

### Opción 3: Ver la Base de Datos
```bash
make shell-db

# Luego en psql:
\dt                        # Ver tablas
SELECT * FROM orders;      # Ver órdenes
SELECT * FROM metrics;     # Ver métricas
\q                         # Salir
```

## 🆘 Solución de Problemas

### ❌ Error: "Port 8080 already in use"
```bash
# Matar proceso en puerto 8080
lsof -ti:8080 | xargs kill -9
```

### ❌ Error: "Cannot connect to Docker daemon"
```bash
# Asegúrate de que Docker Desktop esté corriendo
# Reinicia Docker Desktop
```

### ❌ Error: "Binance API credentials not configured"
- Verifica que `.env` tenga las claves correctas
- No dejes espacios alrededor del `=`
- Las claves NO deben tener comillas

### ❌ Frontend muestra "Loading..." infinito
```bash
# Ver logs del backend
make logs-backend

# Verificar que el backend está running
curl http://localhost:8080/healthz
```

## 📖 Leer Más

- [README Completo](./README.md) - Documentación exhaustiva
- [Configuración Avanzada](./README.md#configuración-del-sistema)
- [Agregar Estrategias](./README.md#agregar-nuevas-estrategias)

## 🎓 Tips para Principiantes

1. **Siempre empieza con testnet**: No uses dinero real hasta dominar el sistema
2. **Backtest primero**: Antes de paper trading, corre backtests
3. **Monitorea los logs**: `make logs` es tu mejor amigo
4. **Lee las métricas**: Sharpe, MaxDD, Win Rate son clave
5. **Kill-switch a mano**: Conoce cómo detener todo: botón rojo en dashboard

## ⚠️ Advertencias Importantes

- 🚫 **NUNCA** compartas tu `.env`
- 🚫 **NUNCA** uses live mode sin probar exhaustivamente en paper
- 🚫 **NUNCA** inviertas más de lo que puedes perder
- ✅ **SIEMPRE** monitorea el sistema cuando esté corriendo
- ✅ **SIEMPRE** ten el kill-switch accesible

---

**¿Listo?** Ejecuta `make dev` y empieza tu viaje en trading algorítmico! 🚀

