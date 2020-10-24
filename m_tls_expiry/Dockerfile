## Containerized active itemlog monitor
# Koko 2020
FROM ubuntu

# Install Dependencies
RUN apt update && apt install -y \
	python3 \
	python3-pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Environment Placeholders
ENV POLL_INTERVAL=900
ENV PROMETHEUS_PORT=80

# Copy Script
COPY monitor_tls_expiry.py monitor_tls_expiry.py

CMD ["python3", "monitor_tls_expiry.py"]
