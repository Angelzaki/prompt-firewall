FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY templates ./templates
COPY static ./static
COPY samples ./samples
COPY tests ./tests

RUN pip install --no-cache-dir -e . \
 && mkdir -p results

EXPOSE 8011

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8011/health')" || exit 1

ENTRYPOINT ["python", "-m", "prompt_firewall"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8011"]
