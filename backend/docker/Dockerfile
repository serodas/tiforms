FROM python:3.11-bullseye

# Variables de entorno para ODBC y Poetry
ENV LD_LIBRARY_PATH=/opt/ibm/iaccess/lib64:$LD_LIBRARY_PATH
ENV ODBCINI=/etc/odbc.ini
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# 1️⃣ Instalar dependencias del sistema + wkhtmltopdf + IBM iAccess en un solo RUN
COPY ./docker/odbc/ibm-iaccess-1.1.0.12-1.0.amd64.deb /tmp/
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc g++ python3-dev libxml2-dev unixodbc-dev \
        curl make libaio1 wget gnupg2 ca-certificates gettext-base \
        libpangocairo-1.0-0 libpangoft2-1.0-0 libpango-1.0-0 libcairo2 \
        fonts-liberation nginx \
        fontconfig libfreetype6 libjpeg62-turbo libpng16-16 \
        libx11-6 libxcb1 libxext6 libxrender1 \
        xfonts-75dpi xfonts-base \
    && wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && apt install -y ./wkhtmltox_0.12.6.1-2.bullseye_amd64.deb \
    && dpkg -i /tmp/ibm-iaccess-1.1.0.12-1.0.amd64.deb || apt-get install -f -y \
    && rm -rf /var/lib/apt/lists/* /tmp/*.deb

# 2️⃣ Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# 3️⃣ Copiar solo archivos de dependencias y cachear instalación
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# 4️⃣ Copiar el resto del código
COPY . .

# 5️⃣ Configuraciones finales
COPY ./docker/odbc/odbc.ini.template /etc/odbc.ini.template
COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY ./docker/nginx/default.conf /etc/nginx/conf.d/default.conf

ENTRYPOINT ["/entrypoint.sh"]

CMD gunicorn app.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers 3 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 60 \
    --graceful-timeout 20 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
