select *
from {{ source('telemetry', 'telemetry_clean') }}
where heart_rate < 20
   or heart_rate > 300