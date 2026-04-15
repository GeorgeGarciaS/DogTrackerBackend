select *
from {{ source('telemetry', 'telemetry_raw') }}
where cumulative_steps < 0