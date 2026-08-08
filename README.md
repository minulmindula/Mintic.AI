# Mintic.AI

> **Agentic Multi-Modal AI Trading Platform**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license) [![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)](#requirements) [![Status](https://img.shields.io/badge/status-alpha-yellow)](#status)

**Mintic.AI** is an agentic, multi-modal framework for researching, backtesting, and deploying AI-driven trading strategies. It chains autonomous agents to process market data, news text, orderbooks, and chart images into automated trading signals and risk-managed execution.

---

## Key Features

- **Agentic Workflows:** Chain modular agents (`DataAgent`, `AlphaAgent`, `RiskAgent`, `ExecAgent`).
- **Multi-Modal Pipeline:** Ingest OHLCV data, orderbook snapshots, news sentiment, and chart visual features.
- **Event-Driven Backtester:** Historical replay engine with built-in P&L, drawdown, and performance tracking.
- **Execution & Safety:** Modular broker adapters (paper/live) with position limits and circuit breakers.

---

## Tech Stack

- **Backend:** Python 3.10+ (FastAPI, PyTorch/scikit-learn)
- **Frontend:** TypeScript + HTML (Optional Web Dashboard)
- **DevOps & Data:** Docker, Docker Compose, Parquet/CSV, Time-Series DBs

---

## Getting Started

### Prerequisites
- **Python:** 3.10 or higher
- **Node.js:** 18+ (Optional, for web dashboard)
- **Docker:** Recommended for isolated runs

### 1. Installation

```bash
# Clone the repository
git clone [https://github.com/minulmindula/Mintic.AI.git](https://github.com/minulmindula/Mintic.AI.git)
cd Mintic.AI

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
