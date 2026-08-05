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