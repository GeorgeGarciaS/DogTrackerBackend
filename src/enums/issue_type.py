from enum import Enum


class IssueType(str, Enum):
    LATITUDE_OUT_OF_RANGE = "latitude_out_of_range"
    LONGITUDE_OUT_OF_RANGE = "longitude_out_of_range"
    HEART_RATE_INVALID = "heart_rate_invalid"
    BATTERY_OUT_OF_RANGE = "battery_out_of_range"
    DUPLICATE_EVENT = "duplicate_event"