# tesp-api

## Local development

### Poetry
See the [poetry docs](https://python-poetry.org/docs/) for information on how to add/update dependencies.
Create the virtual environment and install dependencies with:

```shell
poetry install
```

Start a development server locally:

```shell
poetry run uvicorn app.main:app --reload --host localhost --port 8000
```