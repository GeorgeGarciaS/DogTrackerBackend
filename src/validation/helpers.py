def validate_latitude(latitude) -> bool:
    if (-90 <= latitude <= 90):
        return True
    return False

def validate_longitude(longitude) -> bool:
    if (-180 <= longitude <= 180):
        return True
    return False
