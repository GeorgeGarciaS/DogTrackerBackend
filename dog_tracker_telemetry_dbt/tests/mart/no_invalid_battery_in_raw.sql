select *
from {{ source('telemetry', 'telemetry_raw') }}
where battery < 0
   or battery > 100