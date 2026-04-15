with raw as (

    select
        event_id,
        dog_id,
        latitude,
        longitude,
        signal_strength
    from {{ source('telemetry', 'telemetry_raw') }}

),

dq as (

    select distinct
        event_id,
        1 as is_rejected
    from {{ source('telemetry', 'data_quality_issues') }}

)

select
    r.event_id,
    r.dog_id,
    r.latitude,
    r.longitude,
    r.signal_strength,
    coalesce(dq.is_rejected, 0) as is_rejected
from raw r
left join dq
    on r.event_id = dq.event_id