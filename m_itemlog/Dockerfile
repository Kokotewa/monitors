## Containerized active itemlog monitor
# Koko 2020
FROM ubuntu

# Dependencies
RUN apt update
RUN apt install -y \
	python3 \
	python3-pip
RUN pip3 install pymssql prometheus_client

# Environment Placeholders
ENV DB_HOSTNAME='' 
ENV DB_DATABASE=''
ENV DB_USERNAME=''
ENV POLL_INTERVAL=720
ENV PROMETHEUS_PORT=80

# Copy Script
COPY monitor_itemlog.py monitor_itemlog.py

# Executable
CMD ["python3", "monitor_itemlog.py"]
