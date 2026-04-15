select *
from {{ source('telemetry', 'telemetry_raw') }}
where latitude < {{ env_var('BOUNDARY_MIN_LAT') | float }}
   or latitude > {{ env_var('BOUNDARY_MAX_LAT') | float }}
   or longitude < {{ env_var('BOUNDARY_MIN_LON') | float }}
   or longitude > {{ env_var('BOUNDARY_MAX_LON') | float }}