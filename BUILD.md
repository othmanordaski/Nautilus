# Build and Distribution Guide

## Building the Package

```bash
# Install build tools
pip install build twine

# Build the distribution
python -m build

# This creates:
# - dist/nautilus_stream-1.0.0.tar.gz (source distribution)
# - dist/nautilus_stream-1.0.0-py3-none-any.whl (wheel)
```

## Testing Installation

```bash
# Install from local build
pip install dist/nautilus_stream-1.0.0-py3-none-any.whl

# Or install in editable mode for development
pip install -e .
```

## Publishing to PyPI (Test)

```bash
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ nautilus-stream
```

## Publishing to PyPI (Production)

```bash
# Upload to PyPI
python -m twine upload dist/*

# Users can then install with:
pip install nautilus-stream
```

## Version Management

Update version in:
1. `__version__.py`
2. `pyproject.toml`
3. `CHANGELOG.md`

Then rebuild and republish.
