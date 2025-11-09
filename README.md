# NexiTrade - Sistema Autónomo de Trading Cripto con IA

> **⚠️ ADVERTENCIA**: Este es un sistema de trading algorítmico. El trading conlleva riesgos significativos. Nunca promete rendimientos. Siempre comienza con paper trading y entiende completamente el sistema antes de usar dinero real.

## 🎯 Características

- **Trading Autónomo Multi-Estrategia**: Trend following, mean reversion, breakout, market making, grid
- **IA/ML/RL**: Modelos ensemble (XGBoost, LightGBM, RF), calibración de probabilidades, RL-PPO para sizing
- **Gestión de Riesgo Robusta**: Circuit breakers, límites de exposición, stops dinámicos, max drawdown
- **Multi-Exchange**: Binance (CEX) + Uniswap v3 (DEX EVM)
- **3 Modos**: Backtest con walk-forward, Paper trading, Live trading
- **Dashboard Web**: Next.js con métricas en tiempo real, gráficos, control de estrategias
- **Calidad de Producción**: TypeScript, logs JSON estructurados, tests, Docker Compose

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  Dashboard │ Charts │ Orders │ Risk Controls │ Kill Switch  │
└────────────────────────┬────────────────────────────────────┘
                         │ REST + WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                   Backend (FastAPI + Python)                 │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Strategies  │  │  ML/RL       │  │  Risk Mgmt   │     │
│  │  - Trend ATR │  │  - Ensemble  │  │  - Circuit   │     │
│  │  - Mean Rev  │  │  - PPO Agent │  │  - Limits    │     │
│  │  - Breakout  │  │  - Features  │  │  - Sizing    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Execution   │  │  Portfolio   │  │  Datafeed    │     │
│  │  - Router    │  │  - Allocator │  │  - OHLCV     │     │
│  │  - Fees      │  │  - Rebalance │  │  - WebSocket │     │
│  │  - Slippage  │  │  - PnL       │  │  - Ticker    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Exchanges   │  │  Backtest    │  │  Paper       │     │
│  │  - Binance   │  │  - Vectorbt  │  │  - Broker    │     │
│  │  - Uniswap   │  │  - Walk-Fwd  │  │  - Simulator │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     PostgreSQL Database                      │
│  Orders │ Trades │ Positions │ Equity │ Metrics │ ML Data   │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Requisitos

- Docker y Docker Compose
- (Opcional) Python 3.11+ y Node.js 20+ para desarrollo local

## 🚀 Inicio Rápido

### 1. Clonar y Configurar

```bash
# Clonar el repositorio (o descargar)
cd "BOT CRYPTO"

# Copiar y configurar .env
cp .env.template .env
# Editar .env con tus credenciales
```

### 2. Configurar `.env`

Edita el archivo `.env` con tus credenciales:

```bash
# Binance API (obtener de https://www.binance.com/en/my/settings/api-management)
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_SECRET=tu_secret_aqui
BINANCE_TESTNET=true  # Usar testnet para pruebas

# EVM/DEX (opcional, solo si usarás DEX)
EVM_PRIVATE_KEY=0xtu_private_key
RPC_URL=https://eth-mainnet.g.alchemy.com/v2/tu-api-key

# Seguridad (cambiar a tokens seguros)
ADMIN_TOKEN=genera_un_token_largo_y_aleatorio_minimo_64_caracteres
JWT_SECRET=genera_otro_token_largo_y_aleatorio_minimo_64_caracteres

# Base de datos (puedes dejar por defecto)
POSTGRES_PASSWORD=cambia_esto_por_seguridad
```

### 3. Levantar el Sistema

```bash
# Construir e iniciar todos los servicios
make dev

# O manualmente:
docker-compose up --build
```

Esto levantará:
- **Backend**: http://localhost:8080 (API)
- **Frontend**: http://localhost:3001 (Dashboard)
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6380

### 4. Verificar que Funciona

```bash
# Ver logs
make logs

# Verificar estado
curl http://localhost:8080/healthz

# Abrir dashboard
open http://localhost:3001
```

## 📖 Guías de Uso

### Backtest (Recomendado como Primer Paso)

```bash
# Ejecutar backtests de todas las estrategias habilitadas
make backtest

# Ver resultados en logs o database
```

Edita `app/backend/config/system.yaml` para configurar:
- Periodo de backtest (`start_date`, `end_date`)
- Walk-forward settings
- Estrategias a testear

### Paper Trading (Simulación Sin Riesgo)

```bash
# Iniciar paper trading
make paper
```

El paper trading:
- Simula ejecución de órdenes con slippage y fees realistas
- No ejecuta órdenes reales
- Guarda todas las métricas en base de datos
- Ideal para validar estrategias en condiciones reales

### Live Trading (⚠️ DINERO REAL)

```bash
# Requiere confirmación explícita
make live
# Te pedirá escribir: i-know-what-im-doing
```

**ANTES de activar live trading:**
1. ✅ Ejecuta backtests exhaustivos
2. ✅ Prueba en paper trading al menos 1 semana
3. ✅ Verifica que las métricas OOS superan umbrales mínimos
4. ✅ Comienza con capital pequeño
5. ✅ Monitorea constantemente el dashboard
6. ✅ Ten el kill-switch a mano

## ⚙️ Configuración del Sistema

### `app/backend/config/system.yaml`

Archivo principal de configuración. Ejemplo comentado:

```yaml
mode: paper  # backtest | paper | live

symbols:
  - "BTC/USDT"
  - "ETH/USDT"

timeframe: "1m"
capital: 20000
fees_bps: 10      # 0.10%
slippage_bps: 2   # 0.02%

risk:
  risk_per_trade: 0.003           # 0.3% por operación
  max_daily_drawdown: 0.04        # 4% hard-stop diario
  max_trades_per_minute: 6
  max_trades_per_day: 1200
  max_position_exposure_pct: 25   # 25% por activo
  max_total_exposure_pct: 80      # 80% total

portfolio:
  allocator: "risk_parity"  # equal_weight | risk_parity | momentum
  target_vol_annual: 0.25
  rebalance_hours: 12
  cost_aware: true

strategies:
  trend_atr:
    enabled: true
    sma_fast: 50
    sma_slow: 200
    atr_mult_sl: 2.0
    atr_mult_tp: 2.0
    atr_trailing: 1.0
    
  meanrev_rsi:
    enabled: true
    rsi_th: 30
    rsi_period: 14
    bb_period: 20
    bb_std: 2.0
    min_rr: 1.5

ml:
  ensemble:
    enabled: true
    horizon_bars: 1
    min_confidence: 0.58
    max_turnover_per_day: 3.0
    models:
      - xgboost
      - lightgbm
      - random_forest

rl:
  ppo_sizer:
    enabled: true
    size_bounds_pct_equity: [0.0, 0.01]
    reward:
      pnl_weight: 1.0
      dd_penalty: 4.0
      fee_penalty: 2.0
```

## 🔐 Seguridad

### Nunca Expongas Claves

- ❌ **NUNCA** commites `.env` a git
- ❌ **NUNCA** expongas claves en el frontend
- ✅ Todas las claves están en `.env` (backend only)
- ✅ Firma de transacciones solo en backend
- ✅ Endpoints mutantes protegidos con `ADMIN_TOKEN`

### Binance API

Configurar permisos mínimos necesarios:
- ✅ Enable Reading
- ✅ Enable Spot & Margin Trading (si es necesario)
- ❌ Disable Withdrawals
- ✅ Restrict API to IP (recomendado)

### EVM Private Key

- Solo requerida para DEX trading
- Se usa para firmar transacciones en backend
- Considera usar wallet separada con fondos limitados

## 📊 Gestión de Riesgo

### Circuit Breakers (Corta-Circuitos)

Se activan automáticamente si:
- **Max Daily Drawdown**: Pérdida diaria > 4% (configurable)
- **Failed Orders**: Demasiados errores de ejecución
- **Exchange Issues**: Problemas de conectividad

Cuando se activa:
- 🛑 Se detienen TODAS las operaciones nuevas
- 🔄 Se cierran posiciones abiertas (opcional)
- ⏱️ Cooldown period antes de poder reanudar
- 🔧 Requiere reset manual o esperar cooldown

### Kill Switch Manual

Desde el dashboard o API:

```bash
# Via curl
curl -X POST http://localhost:8080/api/kill \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Via dashboard
# Click en botón "EMERGENCY STOP"
```

### Límites de Riesgo

- **Position Sizing**: Máximo 0.3% de equity por trade (default)
- **Max Position Exposure**: 25% del capital por activo
- **Max Total Exposure**: 80% del capital total
- **Rate Limits**: 6 trades/minuto, 1200 trades/día

## 🧪 Tests

```bash
# Ejecutar todos los tests
make test

# Tests específicos
docker-compose exec backend pytest tests/test_circuit_breakers.py -v
docker-compose exec backend pytest tests/test_risk_limits.py -v
docker-compose exec backend pytest tests/test_paper_broker.py -v
```

## 📈 Métricas de Performance

El sistema calcula y trackea:

- **Sharpe Ratio**: Return ajustado por volatilidad
- **Sortino Ratio**: Return ajustado por downside volatility
- **Max Drawdown**: Máxima caída desde peak
- **Calmar Ratio**: CAGR / Max Drawdown
- **Win Rate**: % de trades ganadores
- **Profit Factor**: Gross profit / Gross loss
- **Turnover**: Frecuencia de operaciones

## 🔧 Comandos Útiles del Makefile

```bash
make dev           # Levantar todo el sistema
make up            # Levantar sin rebuild
make down          # Detener servicios
make logs          # Ver logs en vivo
make logs-backend  # Ver solo logs del backend

make migrate       # Aplicar migraciones de DB
make backtest      # Correr backtests
make paper         # Iniciar paper trading
make live          # Iniciar live trading (con confirmación)

make test          # Ejecutar tests
make lint          # Linter
make format        # Formatear código

make seed          # Descargar datos históricos
make status        # Ver estado del sistema
make stop-trading  # Activar kill-switch

make shell-backend # Shell en contenedor backend
make shell-db      # psql en base de datos

make reset-db      # ⚠️ Resetear DB (BORRA TODO)
```

## 🎓 Agregar Nuevas Estrategias

### 1. Crear Archivo de Estrategia

```python
# app/backend/strategies/mi_estrategia.py
from .base import BaseStrategy, Signal
import pandas as pd

class MiEstrategia(BaseStrategy):
    def __init__(self, config: dict):
        super().__init__("mi_estrategia", config)
        self.param1 = config.get("param1", 10)
    
    def generate_signals(self, symbol: str, data: pd.DataFrame) -> list[Signal]:
        # Tu lógica aquí
        if condicion_compra:
            return [Signal(
                symbol=symbol,
                side="buy",
                entry_price=data['close'].iloc[-1],
                stop_loss=calcular_stop(),
                take_profit=calcular_tp(),
                confidence=0.85,
                reason="Mi condición de compra",
            )]
        return []
```

### 2. Registrar en `strategies/__init__.py`

```python
from .mi_estrategia import MiEstrategia

__all__ = [..., "MiEstrategia"]
```

### 3. Agregar a `system.yaml`

```yaml
strategies:
  mi_estrategia:
    enabled: true
    param1: 20
    param2: 0.5
```

### 4. Integrar en Engine

Editar el motor de trading para cargar y ejecutar tu estrategia.

## 🧠 ML/RL Pipeline (Avanzado)

### Feature Engineering

```python
# app/backend/ml/features.py
from ml.features import FeatureEngineer

features_df = FeatureEngineer.generate_features(ohlcv_df)
# Genera: returns, volatility, ATR, RSI, BB%, volume ratios, z-scores
```

### Entrenar Modelos

```bash
# Descargar datos históricos
make seed

# Entrenar ensemble + RL agent
docker-compose exec backend python -m scripts.train_models
```

Los modelos entrenados se guardan en `/models` y se trackean en la tabla `experiments`.

### Criterios de Despliegue

Solo desplegar a paper/live si en **out-of-sample**:
- Sharpe Ratio ≥ 1.0
- Max Drawdown ≤ threshold
- Turnover sostenible (no overtrade)
- Win-rate calibrado con confidence threshold

## 🌐 Conectar Exchanges

### Binance

1. Crear cuenta en [Binance](https://www.binance.com)
2. Generar API Key: Account > API Management
3. Configurar en `.env`:
   ```bash
   BINANCE_API_KEY=tu_key
   BINANCE_SECRET=tu_secret
   BINANCE_TESTNET=true  # Para testnet spot
   ```
4. Para testnet: [testnet.binance.vision](https://testnet.binance.vision/)

### Uniswap (DEX en EVM)

1. Tener wallet con ETH (o token nativo del chain)
2. Exportar private key (⚠️ usar wallet de testing)
3. Configurar RPC (Alchemy, Infura, o nodo propio)
4. En `.env`:
   ```bash
   EVM_PRIVATE_KEY=0xtu_private_key
   RPC_URL=https://eth-mainnet.g.alchemy.com/v2/API_KEY
   CHAIN_ID=1  # 1=Ethereum, 137=Polygon, etc.
   ```

**Nota**: La integración DEX es básica. Producción requiere:
- Oracle de precios (Chainlink, Uniswap TWAP)
- Gestión de gas automática
- Protección MEV
- Event monitoring para fills

## 📚 Recursos y Referencias

### Trading Algorítmico
- [Quantopian Lectures](https://www.quantopian.com/lectures)
- [QuantStart](https://www.quantstart.com/)

### Machine Learning para Trading
- [Advances in Financial Machine Learning](https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086) - Marcos López de Prado

### Risk Management
- [Risk Management for Traders](https://www.investopedia.com/risk-management-4427755)

### APIs
- [Binance API Docs](https://binance-docs.github.io/apidocs/)
- [CCXT Documentation](https://docs.ccxt.com/)
- [Web3.py Docs](https://web3py.readthedocs.io/)

## ⚠️ Disclaimer

**RENUNCIA DE RESPONSABILIDAD**

Este software se proporciona "TAL CUAL", sin garantías de ningún tipo. El trading de criptomonedas conlleva riesgos sustanciales, incluyendo la pérdida total del capital invertido.

- ❌ No se garantiza ningún rendimiento
- ❌ No es asesoramiento financiero
- ❌ Los resultados pasados no garantizan resultados futuros
- ❌ Puede perder más de lo invertido (en apalancamiento)
- ✅ Use bajo su propio riesgo
- ✅ Comience con capital que puede permitirse perder
- ✅ Siempre pruebe exhaustivamente en paper trading primero

Los autores no se hacen responsables de pérdidas financieras derivadas del uso de este software.

## 🤝 Contribuir

Las contribuciones son bienvenidas:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Asegúrate de que los tests pasan: `make test`
4. Formatea el código: `make format`
5. Commit y push
6. Abre un Pull Request

## 📧 Soporte

Para preguntas o issues:
- Abre un issue en GitHub
- Lee la documentación completa
- Revisa los logs: `make logs`

## 📄 Licencia

Este proyecto es de código abierto. Ver LICENSE para detalles.

---

**Desarrollado con ❤️ para la comunidad de trading algorítmico**

*Versión: 1.0.0*

