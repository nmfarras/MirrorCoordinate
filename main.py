import re
import math

def dms_to_decimal(dms_str):
    """Convert DMS (degrees, minutes, seconds) to decimal degrees."""
    match = re.match(r"COORD:([NS])(\d+)\.(\d+)\.(\d+)\.(\d+):([EW])(\d+)\.(\d+)\.(\d+)\.(\d+)", dms_str)
    if not match:
        raise ValueError(f"Invalid DMS format: {dms_str}")
    
    lat_dir, lat_deg, lat_min, lat_sec, lat_msec, lon_dir, lon_deg, lon_min, lon_sec, lon_msec = match.groups()
    lat = int(lat_deg) + int(lat_min) / 60 + int(lat_sec) / 3600 + int(lat_msec) / 3600000
    lon = int(lon_deg) + int(lon_min) / 60 + int(lon_sec) / 3600 + int(lon_msec) / 3600000
    
    if lat_dir == 'S':
        lat = -lat
    if lon_dir == 'W':
        lon = -lon
    
    return lat, lon

def decimal_to_dms(lat, lon):
    """Convert decimal degrees to DMS (degrees, minutes, seconds)."""
    def to_dms(value, direction_positive, direction_negative):
        direction = direction_positive if value >= 0 else direction_negative
        value = abs(value)
        degrees = int(value)
        minutes = int((value - degrees) * 60)
        seconds = int((value - degrees - minutes / 60) * 3600)
        milliseconds = int((value - degrees - minutes / 60 - seconds / 3600) * 3600000)
        return f"{direction}{degrees:03d}.{minutes:02d}.{seconds:02d}.{milliseconds:03d}"
    
    lat_dms = to_dms(lat, 'N', 'S')
    lon_dms = to_dms(lon, 'E', 'W')
    return f"COORD:{lat_dms}:{lon_dms}"

def mirror_coordinate(lat, lon, ref_lat, ref_lon, angle):
    """Mirror a coordinate (lat, lon) about a rotated line through (ref_lat, ref_lon)."""
    # If the coordinate is exactly the reference point, return it unchanged
    if math.isclose(lat, ref_lat, abs_tol=1e-9) and math.isclose(lon, ref_lon, abs_tol=1e-9):
        return lat, lon
    
    # Convert angle to radians
    angle_rad = math.radians(angle)
    
    # Translate to origin
    lat -= ref_lat
    lon -= ref_lon
    
    # Rotate coordinates to align the mirror line with the y-axis
    lat_rot = lat * math.cos(angle_rad) + lon * math.sin(angle_rad)
    lon_rot = -lat * math.sin(angle_rad) + lon * math.cos(angle_rad)
    
    # Mirror about the y-axis
    lon_mirrored = -lon_rot
    
    # Rotate back and translate to original position
    lat_mirrored = lat_rot * math.cos(-angle_rad) + lon_mirrored * math.sin(-angle_rad) + ref_lat
    lon_mirrored = -lat_rot * math.sin(-angle_rad) + lon_mirrored * math.cos(-angle_rad) + ref_lon
    
    return lat_mirrored, lon_mirrored

def process_coordinates(coord_list, ref_coord, angle):
    """Process a list of coordinates to mirror them."""
    ref_lat, ref_lon = dms_to_decimal(ref_coord)
    mirrored_coords = []
    for coord in coord_list:
        try:
            lat, lon = dms_to_decimal(coord)
            mirrored_lat, mirrored_lon = mirror_coordinate(lat, lon, ref_lat, ref_lon, angle)
            mirrored_coords.append(decimal_to_dms(mirrored_lat, mirrored_lon))
        except ValueError as e:
            print(f"Skipping invalid coordinate: {coord}. Error: {e}")
    return mirrored_coords

# Example input
coordinates = [
    "COORD:S008.44.47.005:E115.10.34.143",
    "COORD:S008.44.46.759:E115.10.40.182",
    "COORD:S008.45.00.000:E115.10.00.000"  # This matches reference and should remain unchanged
]
reference_coordinate = "COORD:S008.45.00.000:E115.10.00.000"
rotation_angle = 0  # Rotation angle in degrees, 0 for north-south axis

mirrored = process_coordinates(coordinates, reference_coordinate, rotation_angle)
for coord in mirrored:
    print(coord)
