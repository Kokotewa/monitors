## Containerized active player monitor
#
# Koko 2020
# v1.0.0 - Jan 22 2020 - Koko
FROM ubuntu

# Dependencies
RUN apt update
RUN apt install -y \
	python3 \
	python3-pip
RUN pip3 install pymssql prometheus_client

# Environment Placeholders
ENV DB_HOSTNAME = '' 
ENV DB_DATABASE = ''
ENV DB_USERNAME = ''
ENV DB_PASSWORD = ''
ENV POLL_INTERVAL = 720

# Copy Script
COPY monitor_active.py monitor_active.py

# Executable
CMD ["python3", "monitor_active.py"]
