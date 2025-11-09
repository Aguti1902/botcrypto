# 🚀 Deploy NexiTrade - Vercel + Railway

## 📋 Paso 1: Railway (Backend + Database)

### 1.1 Crear cuenta en Railway
- Ve a: https://railway.app
- Sign up con GitHub

### 1.2 Crear nuevo proyecto
```bash
# Click en "New Project"
# Selecciona "Deploy from GitHub repo"
# Conecta tu GitHub y selecciona este repositorio
```

### 1.3 Añadir PostgreSQL
```bash
# En tu proyecto Railway:
# Click "New" → "Database" → "Add PostgreSQL"
```

### 1.4 Añadir Redis
```bash
# Click "New" → "Database" → "Add Redis"
```

### 1.5 Configurar Variables de Entorno

En Railway, ve a tu servicio backend → Variables:

```bash
# Binance
BINANCE_API_KEY=tu_api_key
BINANCE_SECRET=tu_secret
BINANCE_TESTNET=true

# Admin
ADMIN_TOKEN=tu_token_seguro_largo
JWT_SECRET=otro_token_seguro

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=$PORT
LOG_LEVEL=INFO
ENVIRONMENT=production

# PostgreSQL (Railway las configura automáticamente)
# Solo verifica que existan:
# DATABASE_URL
# POSTGRES_USER
# POSTGRES_PASSWORD
# POSTGRES_DB
# POSTGRES_HOST
# POSTGRES_PORT

# Redis (Railway lo configura automáticamente)
# REDIS_URL
```

### 1.6 Deploy
```bash
# Railway hará deploy automáticamente
# Espera 3-5 minutos
# Copia la URL del backend (ej: https://tu-proyecto.up.railway.app)
```

---

## 📋 Paso 2: Vercel (Frontend)

### 2.1 Crear cuenta en Vercel
- Ve a: https://vercel.com
- Sign up con GitHub

### 2.2 Import proyecto
```bash
# Click "Add New" → "Project"
# Import desde GitHub
# Selecciona este repositorio
```

### 2.3 Configurar Build

**Root Directory**: `app/frontend`

**Build Command**: `npm run build`

**Output Directory**: `.next`

**Install Command**: `npm install`

### 2.4 Configurar Variables de Entorno

En Vercel → Settings → Environment Variables:

```bash
NEXT_PUBLIC_API_URL=https://tu-backend.up.railway.app
NEXT_PUBLIC_WS_URL=wss://tu-backend.up.railway.app
```

**⚠️ IMPORTANTE**: Cambia `tu-backend.up.railway.app` por la URL real de Railway

### 2.5 Deploy
```bash
# Click "Deploy"
# Espera 2-3 minutos
# Tu frontend estará en: https://tu-proyecto.vercel.app
```

---

## ✅ Verificación

### Backend (Railway)
```bash
curl https://tu-backend.up.railway.app/healthz
# Debe responder: {"status":"healthy","service":"nexitrade"}
```

### Frontend (Vercel)
```bash
# Abre en navegador:
https://tu-proyecto.vercel.app
```

---

## 🔧 Troubleshooting

### Error: "Module not found"
- Ve a Railway → Settings → Redeploy

### Error: "Database connection failed"
- Verifica que PostgreSQL esté corriendo en Railway
- Verifica las variables `DATABASE_URL` o `POSTGRES_*`

### Frontend no conecta con Backend
- Verifica `NEXT_PUBLIC_API_URL` en Vercel
- Debe ser la URL de Railway (con https://)
- Redeploy frontend en Vercel

### CORS Error
- El backend ya tiene CORS configurado
- Si persiste, añade tu dominio Vercel a `main.py` en `allow_origins`

---

## 💰 Costos

- **Vercel**: Gratis (frontend)
- **Railway**: 
  - $5/mes por el backend
  - PostgreSQL: Incluido
  - Redis: Incluido
  - **Total: ~$5/mes**

---

## 🎯 URLs Finales

Después del deploy tendrás:

- **Frontend**: `https://tu-proyecto.vercel.app`
- **Backend API**: `https://tu-backend.up.railway.app`
- **API Docs**: `https://tu-backend.up.railway.app/docs`

---

## 📱 Siguientes Pasos

1. ✅ Configura tus API keys de Binance reales
2. ✅ Cambia los tokens de seguridad
3. ✅ Prueba el sistema en paper trading
4. ✅ Monitorea los logs en Railway

---

**¿Listo?** Sigue los pasos y en 15 minutos estás online! 🚀

