# Python JSON:API Standard (PyJAS)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/PyJAS)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
![GitHub License](https://img.shields.io/github/license/kmbhm1/PyJAS)
[![codecov](https://codecov.io/github/kmbhm1/PyJAS/graph/badge.svg?token=PYOJPJTOLM)](https://codecov.io/github/kmbhm1/PyJAS)
![PyPI - Downloads](https://img.shields.io/pypi/dm/PyJAS)

**PyJAS** is a Python library that provides seamless integration of the [JSON:API](https://jsonapi.org/) specification with Pydantic and FastAPI. It simplifies the process of building standards-compliant APIs, ensuring consistency and interoperability across your applications.

## Features

- **Standards Compliance:** Adheres strictly to the JSON:API specification.
- **Pydantic Models:** Utilizes Pydantic for data validation and serialization.
- **FastAPI Integration:** Easily integrates with FastAPI to build high-performance APIs.
- **Flexible Configuration:** Customize behaviors to fit your project's requirements.
- **Extensible:** Supports extensions and customizations for advanced use cases.

## Installation

You can install PyJAS via pip:

```bash
pip install pyjas
```

## Quick Start

Here's a simple example of how to integrate PyJAS with Pydantic & FastAPI:

```python
from fastapi import FastAPI
from pyjas.v1_1 import Document, ResourceObject

app = FastAPI()

class Article(ResourceObject):
    type_: str = "articles"
    id_: str
    attributes: dict

@app.get("/articles/{article_id}", response_model=Document)
async def get_article(article_id: str):
    article = Article(id_=article_id, attributes={"title": "PyJAS"})
    return Document(data=article)
```

For a complete example, visit our [Documentation Site](https://kmbhm1.github.io/PyJAS/).

## Documentation

Comprehensive documentation is available on our [MkDocs site](https://kmbhm1.github.io/PyJAS/).

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for more information.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions or support, please open an issue on [GitHub](https://github.com/kmbhm1/PyJAS/issues).


## Acknowledgements

- Inspired by the [JSON specification](https://jsonapi.org/).
- Built using [Pydantic](https://pydantic-docs.helpmanual.io/) & [FastAPI](https://fastapi.tiangolo.com/).
