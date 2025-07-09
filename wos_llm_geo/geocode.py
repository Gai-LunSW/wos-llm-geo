import pandas as pd
import googlemaps
from typing import Iterable, Optional


def geocode_locations(
    input_path: str,
    api_key: str,
    location_column: str = "location",
    output_path: Optional[str] = None,
) -> str:
    """Geocode a CSV file of locations using the Google Maps API."""
    gmaps = googlemaps.Client(key=api_key)
    df = pd.read_csv(input_path)
    latitudes = []
    longitudes = []
    for place in df[location_column].astype(str).fillna(""):
        if not place:
            latitudes.append(None)
            longitudes.append(None)
            continue
        geocode = gmaps.geocode(place)
        if geocode:
            loc = geocode[0]["geometry"]["location"]
            latitudes.append(loc.get("lat"))
            longitudes.append(loc.get("lng"))
        else:
            latitudes.append(None)
            longitudes.append(None)
    df["lat"] = latitudes
    df["lng"] = longitudes
    output_path = output_path or input_path.replace(".csv", "_geocoded.csv")
    df.to_csv(output_path, index=False)
    return output_path
