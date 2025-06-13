# wasmai justfile - handy commands for development

# Run all tests
test:
    uv run python -m pytest tests/ -v

# Run a specific test file
test-file file:
    uv run python -m pytest tests/{{file}} -v

# Format code with ruff (single quotes)
fmt:
    uv run ruff format .

# Check code with ruff linter
lint:
    uv run ruff check .

# Fix linting issues automatically where possible
lint-fix:
    uv run ruff check . --fix

# Run both formatter and linter
check: fmt lint

# Run all checks (format, lint, typecheck)
check-all: fmt lint typecheck

# Install dependencies
install:
    uv sync

# Install dev dependencies
install-dev:
    uv sync --dev

# Run the example script
example:
    uv run python example.py

# Clean up build artifacts and cache
clean:
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    rm -rf .pytest_cache/
    rm -rf .ruff_cache/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Build the package
build:
    uv build

# Show project info
info:
    @echo "wasmai - WASM module builder"
    @echo "Python version: $(python --version)"
    @echo "uv version: $(uv --version)"
    @echo "Dependencies:"
    @uv tree

# Run type checking with mypy
typecheck:
    uv run mypy wasmai/

# Run type checking on tests (more lenient)
typecheck-tests:
    uv run mypy tests/ --disable-error-code=assignment,operator

# Generate WAT files from examples for inspection
generate-wat:
    #!/usr/bin/env bash
    mkdir -p output
    echo "Generating WAT files from examples..."
    uv run python -c "from example import *; examples = [('simple_add', create_simple_module()), ('gc_struct', create_gc_module()), ('threads_atomic', create_threads_module()), ('tail_call', create_tail_call_module())]; [open(f'output/{name}.wat', 'w').write(encode_text(module)) or open(f'output/{name}.wasm', 'wb').write(encode_binary(module)) or print(f'Generated {name}.wat and {name}.wasm') for name, module in examples]"

# Run quick smoke test
smoke:
    @echo "Running smoke test..."
    @uv run python -c "from wasmai import Module, encode_binary; print('Basic import works')"
    @uv run python -c "from wasmai import *; m = Module(); b = encode_binary(m); print(f'Empty module: {len(b)} bytes')"
    @echo "Smoke test passed"

# Show available commands
help:
    @just --list
