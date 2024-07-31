FROM python:3.12-slim

WORKDIR /app

# copy pyproject.toml and install dependencies
COPY pyproject.toml pyproject.toml
# install pdm and dependencies
RUN pip install pdm
RUN pdm install --no-lock
RUN pdm install --no-lock --dev
# install dev dependencies

COPY . .

ENV PYTHONPATH=/app/src
# run the app
CMD ["uvicorn", "money_movement.main:app", "--host", "0.0.0.0", "--port", "8000"]