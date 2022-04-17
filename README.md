# TESP API

[![GitHub issues](https://img.shields.io/github/issues/ndopj/tesp-api)](https://github.com/ndopj/tesp-api/issues)
[![poetry](https://img.shields.io/badge/maintained%20with-poetry-informational.svg)](https://python-poetry.org/)
[![python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/download)
[![last-commit](https://img.shields.io/github/last-commit/ndopj/tesp-api)]()

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

## License

[![license](https://img.shields.io/github/license/ndopj/tesp-api)](https://github.com/ndopj/tesp-api/blob/main/LICENSE.md)
```
Copyright (c) 2022 Norbert Dopjera

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```