"""
TLS certificate expiry monitor
v1.0.0 Koko - 20/10/24
"""
import socket
import ssl
import logging
import datetime
import os
import time
import prometheus_client

if bool(os.getenv('DEBUG')):
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def check_tls_expiry(host):
    """Return hostname TLS certificate expiry datetime object."""
    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=host[0]
        )

    try:
        conn.connect((str(host[0]), int(host[1])))
        tls_info = conn.getpeercert()
        conn.close()

        # Parse cert to find expiry as datetime obj
        time_expires = datetime.datetime.strptime(
            tls_info['notAfter'],
            r'%b %d %H:%M:%S %Y %Z'
            )
    except ConnectionRefusedError:
        logging.error('Unable to connect to %s:%s', host[0], host[1])
        time_expires = datetime.datetime.utcnow()

    return time_expires


def monitor_tls_expiry(host_string, poll_interval):
    """Monitor TLS certificates expiry."""
    # Translate hoststring into sublists
    hosts = host_string.split(',')
    hosts = [host.strip(' ') for host in hosts]
    hosts = [host.split(':') for host in hosts]

    # Init gauge
    gauge = prometheus_client.Gauge(
        name='tls_expiry',
        documentation='Days until TLS certificate expiry',
        labelnames=['domain']
        )

    while True:
        # Report TLS certificate expiry for each host
        time_now = datetime.datetime.utcnow()

        for host in hosts:
            time_expiry = check_tls_expiry(host)
            time_remain = time_expiry - time_now
            logging.info(
                '%s TLS certificate expires in %s days',
                host[0],
                time_remain.days
                )

            gauge.labels(domain=host[0]).set(time_remain.days)

        time.sleep(poll_interval)

if __name__ == '__main__':
    HOST_STRING = str(os.getenv('HOST_STRING'))
    POLL_INTERVAL = int(os.getenv('POLL_INTERVAL'))
    PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT'))

    prometheus_client.start_http_server(PROMETHEUS_PORT)
    monitor_tls_expiry(
        host_string=HOST_STRING,
        poll_interval=POLL_INTERVAL
    )
