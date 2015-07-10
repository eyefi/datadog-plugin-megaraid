This is a plugin for [Datadog](http://docs.datadoghq.com/guides/agent_checks/)
that checks the status of LSI MegaRAID controllers and returns a variety of
gauges for drives and arrays connected to them.

## Gauges

 * `megaraid.drives.total` The total number of physical drives connected to
   the controller.
 * `megaraid.drives.failed` The number of failed physical drives connected
   to the controller.
 * `megaraid.errors.media.total` The total number of media errors aggregated
   across all physical drives connected to the controller.
 * `megaraid.errors.media.maximum` The maximum number of media errors on any
   one physical drive connected to the controller.
 * `megaraid.errors.other.total` The total number of other erros aggregated
   across all physical drives connected to the controller.
 * `megaraid.errors.other.maximum` The maximum number of other errors on any
   one physical drive connected to the controller.
 * `megaraid.arrays.total` The total number of virtual drives configured on
   the controller.
 * `megaraid.arrays.optimal` The number of arrays that are in optimal
   operating status.
 * `megaraid.arrays.degraded` The number of arrays that are in degrated
   operating status.
 * `megaraid.arrays.unknown` The number of arrays that are in unknown
   operating status.
