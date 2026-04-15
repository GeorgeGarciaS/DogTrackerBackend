select *
from {{ source('telemetry', 'telemetry_raw') }}
where signal_strength < 0
   or signal_strength > 100