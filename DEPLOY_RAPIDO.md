# ⚡ Deploy RÁPIDO - 5 Pasos

## 1️⃣ Railway (Backend) - 5 min

1. Ve a https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Conecta este repo
4. Click en el proyecto → "New" → "Add PostgreSQL"
5. Click en el proyecto → "New" → "Add Redis"
6. Click en tu servicio backend → "Variables" → Añade:

```bash
BINANCE_API_KEY=tu_key
BINANCE_SECRET=tu_secret
BINANCE_TESTNET=true
ADMIN_TOKEN=token_largo_seguro_123456
JWT_SECRET=otro_token_654321
BACKEND_HOST=0.0.0.0
LOG_LEVEL=INFO
ENVIRONMENT=production
```

7. Railway desplegará automáticamente
8. **COPIA LA URL** (algo como: `https://nexitrade-production.up.railway.app`)

---

## 2️⃣ Vercel (Frontend) - 3 min

1. Ve a https://vercel.com
2. "Add New" → "Project"
3. Import este repo desde GitHub
4. Configuración:
   - **Root Directory**: `app/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

5. **Environment Variables**:
```bash
NEXT_PUBLIC_API_URL=https://TU-URL-DE-RAILWAY.up.railway.app
NEXT_PUBLIC_WS_URL=wss://TU-URL-DE-RAILWAY.up.railway.app
```

6. Click "Deploy"

---

## ✅ Listo!

- **Frontend**: https://tu-proyecto.vercel.app
- **Backend**: https://tu-proyecto.up.railway.app
- **API Docs**: https://tu-proyecto.up.railway.app/docs

---

## 🐛 Si algo falla:

**Backend no arranca en Railway:**
- Ve a Logs → busca errores
- Verifica que PostgreSQL y Redis estén conectados

**Frontend no conecta:**
- Verifica `NEXT_PUBLIC_API_URL` en Vercel settings
- Debe ser la URL completa de Railway (con `https://`)
- Redeploy el frontend

**CORS error:**
- Ya está configurado para permitir todos los orígenes
- Si persiste, espera 1-2 minutos y recarga

---

💰 **Costo**: ~$5/mes (Railway) | Vercel es gratis

