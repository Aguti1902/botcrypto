#!/bin/bash

echo "🔍 Diagnóstico NexiTrade"
echo "========================"
echo ""

# Check 1: Docker
echo "1️⃣ Verificando Docker..."
if command -v docker &> /dev/null; then
    echo "   ✅ Docker instalado: $(docker --version)"
    if docker ps &> /dev/null; then
        echo "   ✅ Docker daemon corriendo"
    else
        echo "   ❌ Docker daemon NO está corriendo"
        echo "   → Inicia Docker Desktop"
        exit 1
    fi
else
    echo "   ❌ Docker NO instalado"
    echo "   → Instala Docker Desktop desde https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check 2: Docker Compose
echo ""
echo "2️⃣ Verificando Docker Compose..."
if command -v docker-compose &> /dev/null; then
    echo "   ✅ Docker Compose instalado: $(docker-compose --version)"
else
    echo "   ❌ Docker Compose NO instalado"
    exit 1
fi

# Check 3: .env file
echo ""
echo "3️⃣ Verificando archivo .env..."
if [ -f .env ]; then
    echo "   ✅ Archivo .env existe"
    
    # Check critical variables
    if grep -q "BINANCE_API_KEY=your_binance" .env; then
        echo "   ⚠️  BINANCE_API_KEY no configurado (todavía tiene valor por defecto)"
    else
        echo "   ✅ BINANCE_API_KEY configurado"
    fi
    
    if grep -q "ADMIN_TOKEN=change_this" .env; then
        echo "   ⚠️  ADMIN_TOKEN no configurado (todavía tiene valor por defecto)"
    else
        echo "   ✅ ADMIN_TOKEN configurado"
    fi
else
    echo "   ❌ Archivo .env NO existe"
    echo "   → Ejecuta: cp .env.template .env"
    echo "   → Luego edita .env con tus credenciales"
    exit 1
fi

# Check 4: Puertos disponibles
echo ""
echo "4️⃣ Verificando puertos disponibles..."
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "   ❌ Puerto $1 en uso por: $(lsof -Pi :$1 -sTCP:LISTEN | tail -n 1 | awk '{print $1}')"
        return 1
    else
        echo "   ✅ Puerto $1 disponible"
        return 0
    fi
}

check_port 3001
check_port 8080
check_port 5433
check_port 6380

# Check 5: Estructura de archivos
echo ""
echo "5️⃣ Verificando estructura de archivos..."
if [ -f docker-compose.yml ]; then
    echo "   ✅ docker-compose.yml existe"
else
    echo "   ❌ docker-compose.yml NO existe"
    exit 1
fi

if [ -f Makefile ]; then
    echo "   ✅ Makefile existe"
else
    echo "   ❌ Makefile NO existe"
fi

if [ -d app/backend ]; then
    echo "   ✅ Directorio app/backend existe"
else
    echo "   ❌ Directorio app/backend NO existe"
    exit 1
fi

if [ -d app/frontend ]; then
    echo "   ✅ Directorio app/frontend existe"
else
    echo "   ❌ Directorio app/frontend NO existe"
    exit 1
fi

# Check 6: Containers running
echo ""
echo "6️⃣ Verificando contenedores Docker..."
if docker ps | grep -q nexitrade; then
    echo "   ✅ Contenedores NexiTrade corriendo:"
    docker ps --filter name=nexitrade --format "      - {{.Names}}: {{.Status}}"
else
    echo "   ℹ️  No hay contenedores NexiTrade corriendo"
    echo "   → Ejecuta: make dev"
fi

echo ""
echo "========================"
echo "✅ Diagnóstico completado"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Corrige cualquier ❌ que veas arriba"
echo "   2. Ejecuta: make dev"
echo "   3. Abre: http://localhost:3001"
echo ""

