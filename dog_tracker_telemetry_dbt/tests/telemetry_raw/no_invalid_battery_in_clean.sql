select *
from {{ source('telemetry', 'telemetry_clean') }}
where battery < 0
   or battery > 100