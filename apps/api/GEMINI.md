# Mintic.AI Engineering Guidelines

## Architecture Rules
- Core modules must reside in `src/core/`.
- Safety Lock logic in `src/core/safety.py` MUST NOT contain any LLM or AI dependencies.
- Strict Pydantic models in `src/core/schemas.py` enforce all inputs/outputs.
- Package manager: `uv`
- Python version: 3.11+

## Code Quality Requirements
- All Pydantic validation rules must be unit-tested in `tests/test_safety.py`.
- Always write type hints for every function.
- Tests must pass using `uv run pytest`.



# Mintic.AI Full-Stack Architecture Rules

## Workspace Layout
- Backend: `apps/api/` (Python 3.11+, FastAPI, Pydantic, uv)
- Frontend: `apps/web/` (Next.js App Router, React, Tailwind CSS, shadcn/ui)

## Frontend Rules
- Use Server Components where possible; use Client Components (`"use client"`) for dynamic agent logs and live WebSocket feeds.
- All API types consumed by Next.js must match the Pydantic schemas defined in `apps/api/src/core/schemas.py`.
- Tailwind CSS styling should adhere to a dark high-contrast trading terminal theme.