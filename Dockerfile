FROM python:3.14-slim AS base
WORKDIR /src/app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.14-slim 
RUN groupadd -r app && useradd -r -g app app
WORKDIR /app
COPY --from=base /install /usr/local
COPY . .
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
ENTRYPOINT [ "python", "-m" ]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]