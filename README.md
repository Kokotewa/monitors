# monitors
A collection of monitors for Aegis Ragnarok Online servers.

Aegis zone servers, especially legacy zone servers, do not readily expose metrics for external consumption.  Fortunately, these metrics can be sourced from the database instead.  Unfortunately, this means the metric update frequency is dependent on the zone server:database sync.  For this reason, the database must be queried for metrics using the zone server synchronization interval.

Koko is from a devops background.  Within the aforementioned background, developers with good intentions mishandled the database.  For this reason all monitors interact with the database via Stored Procedures rather than with full permissions.

Metrics are logged to STDOUT intergrating seamlessly with Docker logs.  Additionally, each monitor supports a prometheus client for metric aggregation.  The `monitors.yaml` file provides an example for deploying a Prometheus/Grafana monitoring stack using Docker Swarm or Docker Compose.

There are some caveats to the `pymssql` client library.  The most important of which is that `pymssql` does not support authentication with usernames inclusive of the `_` character.  For this reason it is recommended to use alphanumeric usernames for monitor accounts.
