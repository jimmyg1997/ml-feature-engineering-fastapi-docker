### Compose shortcuts
up:
    docker-compose up -d

down:
    docker-compose down

build:
    docker-compose build

sh:
    docker-compose run -p 8000:8000 --rm api bash

logs:
    docker-compose logs -f

### Project shortcuts
fast_api:
    docker-compose run --rm api python src/main.py

fast_api_app:
    docker-compose run --rm api uvicorn src.main:app --proxy-headers --host 0.0.0.0 --port 8000


### Network shortcuts
fast_api_net_app : 
	docker run --rm --name app --net=optasia_api_net -p 8000:8000 fastapi_example
