{{ config(materialized='table') }}

{% set cell_size = 0.0002 %}
{% set half_cell = cell_size / 2 %}
{% set boundary_min_lat = env_var('BOUNDARY_MIN_LAT') | float %}
{% set boundary_max_lat = env_var('BOUNDARY_MAX_LAT') | float %}
{% set boundary_min_lon = env_var('BOUNDARY_MIN_LON') | float %}
{% set boundary_max_lon = env_var('BOUNDARY_MAX_LON') | float %}

with base as (

    select
        latitude,
        longitude,
        signal_strength,
        is_rejected
    from {{ ref('stg_telemetry_enriched') }}

),

bucketed as (

    select
        floor(latitude / {{ cell_size }}) * {{ cell_size }} as lat_bucket,
        floor(longitude / {{ cell_size }}) * {{ cell_size }} as lon_bucket,
        signal_strength,
        is_rejected
    from base

),

aggregated as (

    select
        lat_bucket,
        lon_bucket,
        count(*) as total_events,
        sum(is_rejected) as rejected_events,
        avg(signal_strength) as avg_signal
    from bucketed
    group by 1, 2

)

select
    lat_bucket + {{ half_cell }} as center_lat,
    lon_bucket + {{ half_cell }} as center_lon,

    lat_bucket as min_lat,
    lat_bucket + {{ cell_size }} as max_lat,
    lon_bucket as min_lon,
    lon_bucket + {{ cell_size }} as max_lon,

    total_events,
    rejected_events,
    avg_signal,
    rejected_events * 1.0 / total_events as rejection_ratio,

    case
        when rejected_events * 1.0 / total_events > 0.3 then true
        when avg_signal < 30 then true
        else false
    end as is_bad_zone

from aggregated
where total_events >= 3
  and lat_bucket >= {{ boundary_min_lat }}
  and lat_bucket + {{ cell_size }} <= {{ boundary_max_lat }}
  and lon_bucket >= {{ boundary_min_lon }}
  and lon_bucket + {{ cell_size }} <= {{ boundary_max_lon }}