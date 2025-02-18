# use this base image for deployment
FROM arm64v8/python:3.12-alpine
#FROM python:3.12-alpine

# needed deps for installing poetry
RUN apk add --no-cache gcc python3-dev libffi-dev musl-dev

WORKDIR /
ENV POETRY_VERSION=1.7.0
RUN pip install poetry==$POETRY_VERSION
# no need of virtualenvs in docker container
RUN poetry config virtualenvs.create false

COPY ./pyproject.toml ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY ./ ./

CMD ["python", "main.py"]
