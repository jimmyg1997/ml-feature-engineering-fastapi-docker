# pull the official docker image
FROM python:3.8-slim
#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# set work directory
WORKDIR /spp

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
#COPY ./requirements.txt /src/requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy project
#COPY ./src /src
COPY . .
EXPOSE 8000


#COPY ./requirements.txt /code/requirements.txt
#RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
#COPY ./src /code/src
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
