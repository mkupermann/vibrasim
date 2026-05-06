FROM python:3.13-slim

WORKDIR /srv

RUN pip install --no-cache-dir \
    "streamlit>=1.40" \
    "psycopg[binary]>=3.2" \
    "pandas>=2.2"

COPY app /srv/app
COPY db /srv/db

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app/main.py", \
            "--server.address", "0.0.0.0", \
            "--server.port", "8501", \
            "--server.headless", "true", \
            "--browser.gatherUsageStats", "false"]
