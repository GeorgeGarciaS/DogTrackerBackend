select *
from {{ ref('mart_bad_signal_cells') }}
where avg_signal < 0
   or avg_signal > 100