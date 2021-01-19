# monitors
A collection of monitors for Aegis Ragnarok Online servers.

Aegis zone servers, especially zone servers, do not readily expose metrics for external consumption.  Fortunately, these metrics can be sourced from the database instead.  Unfortunately, this means the metric update frequency is dependent on the zone server:database sync.  For this reason, the database must be queried for metrics using the zone server synchronization interval.  

Metrics are logged to STDOUT intergrating seamlessly with Docker logs.  Additionally, each monitor supports a prometheus client for metric aggregation.  The `monitors.yaml` file provides an example for deploying a Prometheus/Grafana monitoring stack using Docker Swarm or Docker Compose.

All monitors interact with the database exclusively through stored procedures.  It is best practice, and recommended, to create a mssql account for each monitor with permissions limited to the associated stored procedure.  However, before doing so, it is important to note that the `pymssql` module does not support authentication with usernames inclusive of the `_` character.  For this reason, it is recommended that mssql monitor accounts consist of alphanumeric characters.
