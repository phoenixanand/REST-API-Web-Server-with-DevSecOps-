FROM python:3.14-slim AS base
WORKDIR /src/app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.14-slim 
RUN groupadd -r app && useradd -r -g app app
WORKDIR /app
COPY --from=base /install /usr/local
COPY . .
USER app
EXPOSE 8000
ENTRYPOINT [ "python", "-m" ]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]