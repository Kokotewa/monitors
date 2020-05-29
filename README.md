# monitors
A collection of monitors for Aegis Ragnarok Online servers.

Aegis zone servers, especially legacy zone servers, do not readily expose metrics for external consumption.  Fortunately, these metrics can be sourced from the database instead.  Unfortunately, this means the metric update frequency is dependent on the zone server:database sync.  For this reason, the database must be queried for metrics using the zone server synchronization interval.

## Metrics
Metrics are logged to STDOUT intergrating seamlessly with Docker logs.  Additionally, each monitor supports a prometheus client for metric aggregation.
