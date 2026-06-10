# FastAPI SLAP2

FastAPI implementation of the IVOA SLAP2 protocol

## Getting Started

Running the project with docker-compose is the recommended way to get started quickly.
By default, the API will be available at `http://localhost:8000/query`.

The VOSI Capabilities endpoint is available at `http://localhost:8000/capabilities`.

Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### Requirements

- Python 3.11+
- [Docker Compose](https://docs.docker.com/compose/) (optional)
- [Conda](https://docs.conda.io/) (optional)

### Running with Docker Compose

```bash
docker-compose up
```

### Running with Conda

```bash
conda env create -f environment.yml
conda activate fastapi-slap2
pip install -e .
uvicorn fastapi_slap2.main:app --reload
```

### Running with pip

```bash
pip install -e .
uvicorn fastapi_slap2.main:app --reload
```

## Implementation

The service is scaffolded for you. To implement your protocol:

1. Define your request/response schemas in `fastapi_slap2/schemas.py`
2. Implement your query logic in `fastapi_slap2/services.py`
3. Add or modify route parameters in `fastapi_slap2/router/slap2_router.py`
4. Update the VOSI capabilities in `fastapi_slap2/router/vosi.py`

## License

See [LICENSE](./LICENSE) for details.
