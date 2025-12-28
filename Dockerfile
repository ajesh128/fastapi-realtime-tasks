FROM python:3.13.3


# Install Poetry
ENV POETRY_VERSION=2.2.0
RUN pip install --upgrade pip && pip install "poetry==$POETRY_VERSION"

# Set working directory
WORKDIR /src/

# Copy Poetry files first for better layer caching
COPY pyproject.toml poetry.lock /src/

# Disable Poetry's virtualenv creation so everything installs system-wide
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi --no-cache



# Copy the rest of the code
COPY app /src/app
COPY Dockerfile /src/Dockerfile

# Expose port (adjust if needed)
EXPOSE 5000

# Entry point for Uvicorn with reload (for dev) or without (for prod)
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
