from enum import Enum

"""
    Shared
"""
LATITUDE_OUT_OF_RANGE = "latitude_out_of_range"
LONGITUDE_OUT_OF_RANGE = "longitude_out_of_range"

"""
    Generic Enums
"""

"""
    Dog Related Enums
"""
class DogErrorType(str, Enum):
    DOG_NOT_FOUND = "dog_not_found"
    INVALID_COORDINATES = "invalid_coordinates"

"""
    Telemetry Related Enums
"""
class TelemetryIssueType(str, Enum):
    HEART_RATE_INVALID = "heart_rate_invalid"
    BATTERY_OUT_OF_RANGE = "battery_out_of_range"
    CUMULATIVE_STEPS_OUT_OF_RANGE = "cumulative_steps_out_of_range"
    DUPLICATE_EVENT = "duplicate_event"
    LATITUDE_OUT_OF_RANGE = LATITUDE_OUT_OF_RANGE
    LONGITUDE_OUT_OF_RANGE = LONGITUDE_OUT_OF_RANGE

class TelemetryStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"

"""
    Data Quality Issue Related Enums
"""
class DataQualityIssueErrorType(str, Enum):
    RECORD_NOT_FOUND = "record_not_found"

