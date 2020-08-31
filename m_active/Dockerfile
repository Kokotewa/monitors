## Containerized active player monitor
# Koko 2020
FROM ubuntu

# Dependencies
RUN apt update && apt install -y \
        python3 \
        python3-pip \
        unixodbc-dev \
        curl

# Install MSSQL Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt update && ACCEPT_EULA=Y apt install -y msodbcsql17
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# MSSQL2012 TLS Workaround
ENV OPENSSL_CONF='/etc/ssl/openssl_custom.cnf'
COPY openssl_custom.cnf /etc/ssl/openssl_custom.cnf

# Install Prometheus Client & pyodbc
RUN pip3 install prometheus_client
RUN pip3 install pyodbc

# Environment Placeholders
ENV DB_HOSTNAME=''
ENV DB_DATABASE=''
ENV DB_USERNAME=''
ENV POLL_INTERVAL=720
ENV PROMETHEUS_PORT=80

# Copy Script
COPY monitor_active.py monitor_active.py

# Executable
CMD ["python3", "monitor_active.py"]
