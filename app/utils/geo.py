import math


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance in kilometers between two coordinates using Haversine formula."""
    R = 6371  # Earth's radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def format_distance(km: float) -> str:
    """Format distance for display."""
    if km < 1:
        return f"{int(km * 1000)} m"
    return f"{km:.1f} km"


def estimate_travel_time(km: float, mode: str = "car") -> int:
    """Estimate travel time in minutes."""
    speeds = {
        "car": 40,       # km/h in urban Mombasa
        "ambulance": 50,  # km/h with sirens
        "walking": 5,     # km/h
    }
    speed = speeds.get(mode, 40)
    return max(1, int((km / speed) * 60))
