# PDF Alchemy

This is the template repo for the CLI tool to manipulate pdfs

**Fork** the project to your github account, this will have the assotiated tests and template to start the project and finish implementation

# Requirements
- Python
- UV
- pymupdf

# Sync and update project packages

```bash
uv sync
```

# Run the tool

1. Initialize `venv`
```bash
uv venv
```

```bash
source .venv/bin/activate
```

2. Run the tool
```bash
uv run main.py
```

# Commands

Se han añadido dos nuevas características al CLI de PDF Alchemy:

1. **Reordenar páginas (`--reorder`)**: Permite reorganizar las páginas de un PDF según una secuencia específica dada por el usuario. 
   * *Ejemplo de uso:* `uv run main.py -f input.pdf -o output.pdf --reorder 4 3 1 2`
2. **Convertir a Imagen (`--to-image`)**: Convierte un rango de páginas o páginas individuales especificadas en imágenes formato PNG (150 DPI).
   * *Ejemplo de uso:* `uv run main.py -f input.pdf -o salida/ --to-image 1-5`

# Run tests

```bash
uv run pytest -q
```

# Compile to a standalone executable

```bash
uv pip install pyinstaller
```

```bash
uv run pyinstaller --onefile main.py
```

> You'll see the new compilation under `dist/`
