select *
from {{ source('telemetry', 'telemetry_clean') }}
where signal_strength < 0
   or signal_strength > 100