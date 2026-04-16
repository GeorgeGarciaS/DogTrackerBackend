select *
from {{ source('telemetry', 'telemetry_clean') }}
where cumulative_steps < 0