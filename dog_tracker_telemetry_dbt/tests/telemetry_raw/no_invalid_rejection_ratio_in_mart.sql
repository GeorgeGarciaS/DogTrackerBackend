select *
from {{ ref('mart_bad_signal_cells') }}
where rejection_ratio < 0
   or rejection_ratio > 1