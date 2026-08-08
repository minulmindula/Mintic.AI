# Mintic.AI

Agentic Multi‑Modal AI Trading Platform

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license) [![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)](#requirements) [![Status](https://img.shields.io/badge/status-alpha-yellow)](#status)

Mintic.AI is an agentic, multi-modal platform for researching, backtesting, and deploying AI-driven trading strategies. It combines agent orchestration, multi-modal data ingestion (market data, news, charts, and alternative data), and modular execution components to enable safe, reproducible algorithmic trading experiments and deployment.

Table of Contents
- Features
- Key Concepts
- Architecture Overview
- Tech Stack
- Getting Started (Quickstart)
- Examples
- Configuration & Environment
- Development
- Testing
- Security & Risk Management
- Contributing
- Roadmap
- License
- Contact

Features
- Agentic workflows: chain reusable agents (data ingestion, signal generation, risk manager, execution) to compose strategies.
- Multi‑modal inputs: OHLCV, orderbook snapshots, news text, sentiment embeddings, chart images.
- Research-first: notebooks, experiment tracking, built-in backtester with event-driven simulation.
- Live trading adapters: modular connectors for paper/live brokers and simulated exchanges.
- Safety and risk controls: position sizing, circuit breakers, max-drawdown limits, supervised overrides.
- Extensible: plugin system for new data sources, models, and execution endpoints.

Key Concepts
- Agent: autonomous module with a defined responsibility (e.g., DataAgent, AlphaAgent, RiskAgent, ExecAgent).
- Strategy: composition of agents plus configuration that defines trading behavior.
- Backtester: event-driven simulator that replays historical data and records P&L and metrics.
- Connector: adapter that implements communication with exchanges/brokers or data providers.
- Multi-modal pipeline: converts heterogeneous inputs into features consumed by models/agents.

Architecture Overview
- Core
  - Agent orchestration layer
  - Strategy manager (compose, version, run)
  - Backtester and live execution engine
- Data
  - Ingestion adapters (CSV, Parquet, REST, websocket)
  - Feature extraction & storage
- Models
  - Model registry (PyTorch/TensorFlow/sklearn)
  - Embedding & image processors
- Integrations
  - Broker connectors (paper/live)
  - Monitoring & logging (Prometheus/Grafana optional)
- UI (optional)
  - Web dashboard for experiment tracking and live monitoring (TypeScript/HTML frontend)

Tech Stack
- Backend: Python (core agents, models, backtester)
- Frontend: TypeScript + HTML (dashboard & controls)
- DevOps: Docker, Docker Compose (local dev & deployments)
- Optional: Node.js tooling for frontend builds
- Data: CSV/Parquet, time-series DBs supported via connectors

Requirements
- Python 3.10+
- Node.js 18+ (for frontend, optional)
- Docker & Docker Compose (recommended for isolated runs)
- (Optional) GPU + CUDA for model training

Quickstart (local)
1. Clone the repo
   - `git clone https://github.com/minulmindula/Mintic.AI.git && cd Mintic.AI`

2. Create a Python venv and install
   - `python -m venv .venv`
   - `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows)
   - `pip install --upgrade pip`
   - `pip install -r requirements.txt`

3. (Optional) Start services with Docker
   - `docker compose up --build`
   - This will start the backend API, front-end dev server (if present), and any local data services.

4. Environment
   - Copy `.env.example` to `.env` and set keys:
     - `DATA_PATH`, `BROKER_API_KEY`, `BROKER_SECRET`, `DATABASE_URL`, etc.
   - For safety, use paper mode credentials or simulated exchanges for experiments.

5. Run the backend (example)
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

6. Run the frontend (if present)
   - `cd frontend`
   - `npm install`
   - `npm run dev`

Examples
- Backtest
  - `python -m mintic.backtest --strategy path/to/strategy.yaml --data data/SPX.parquet --out results/`
- Run a strategy locally (paper)
  - `python -m mintic.runner --strategy my_strategy.yaml --mode paper`
- Notebook experiments
  - Open `notebooks/` and run the provided example notebooks for data prep and model evaluation.

Configuration & Strategy Definition
- Strategies are defined as YAML/JSON files that describe:
  - Agent chain: data -> features -> model -> risk -> execution
  - Parameters: lookback windows, thresholds, risk limits
  - Logging & metrics targets
- Example snippet (strategy.yaml)
