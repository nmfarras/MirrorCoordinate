import re
import math
import matplotlib.pyplot as plt

def dms_to_decimal(dms_str):
    """Convert DMS to decimal degrees."""
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

def mirror_coordinates(coords, ref_lat, ref_lon, angle=0):
    """Mirror a coordinate (lat, lon) about a rotated line through (ref_lat, ref_lon)."""
    
    mirrored = []
    # Convert angle to radians
    angle_rad = math.radians(angle)
    
    for coord in coords:
        lat, lon = dms_to_decimal(coord)
        
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
        
        mirrored.append((lat_mirrored, lon_mirrored))

    return mirrored

def apply_offset(mirrored_coords, ref_coord, final_offset_coord):
    """Move the nearest mirrored coordinate to the final offset coordinate and apply the shift to all."""
    ref_lat, ref_lon = dms_to_decimal(ref_coord)
    final_lat, final_lon = dms_to_decimal(final_offset_coord)

    nearest_lat, nearest_lon = min(mirrored_coords, key=lambda p: math.hypot(p[0] - ref_lat, p[1] - ref_lon))
    
    lat_offset = final_lat - nearest_lat
    lon_offset = final_lon - nearest_lon

    return [(lat + lat_offset, lon + lon_offset) for lat, lon in mirrored_coords]

def plot_coordinates(original, mirrored, mirrored_offset, ref_coord, final_offset_coord):
    """Plot all three coordinate sets with lines connecting corresponding points."""
    plt.figure(figsize=(8, 8))  # Square plot

    # Extract lat/lon for plotting
    orig_lats, orig_lons = zip(*original)
    mirr_lats, mirr_lons = zip(*mirrored)
    off_lats, off_lons = zip(*mirrored_offset)

    # # Plot lines between original and mirrored points
    # for (lat1, lon1), (lat2, lon2) in zip(original, mirrored):
        # plt.plot([lon1, lon2], [lat1, lat2], color='gray', linestyle='dotted', alpha=0.6)

    # # Plot lines between mirrored and mirrored + offset points
    # for (lat1, lon1), (lat2, lon2) in zip(mirrored, mirrored_offset):
        # plt.plot([lon1, lon2], [lat1, lat2], color='gray', linestyle='dotted', alpha=0.6)
        
    # Plot lines
    plt.plot(orig_lons, orig_lats, color='gray', linestyle='dotted', alpha=0.6)
    plt.plot(mirr_lons, mirr_lats, color='gray', linestyle='dotted', alpha=0.6)
    plt.plot(off_lons, off_lats, color='gray', linestyle='dotted', alpha=0.6)

    # Plot original coordinates
    plt.scatter(orig_lons, orig_lats, color='blue', label='Original', marker='o')

    # Plot mirrored coordinates
    plt.scatter(mirr_lons, mirr_lats, color='red', label='Mirrored', marker='x')

    # Plot mirrored & offset coordinates
    plt.scatter(off_lons, off_lats, color='green', label='Mirrored + Offset', marker='s')

    # Reference point & final offset
    ref_lat, ref_lon = dms_to_decimal(ref_coord)
    final_lat, final_lon = dms_to_decimal(final_offset_coord)

    plt.scatter(ref_lon, ref_lat, color='black', label='Reference Point', marker='^')
    plt.scatter(final_lon, final_lat, color='purple', label='Offset Target', marker='*')

    # Adjust aspect ratio to be equal
    plt.axis('equal')  

    # Determine axis limits (same range for x and y)
    all_lats = list(orig_lats) + list(mirr_lats) + list(off_lats) + [ref_lat, final_lat]
    all_lons = list(orig_lons) + list(mirr_lons) + list(off_lons) + [ref_lon, final_lon]
    
    lat_range = max(all_lats) - min(all_lats)
    lon_range = max(all_lons) - min(all_lons)
    
    # Use the larger range for both axes
    max_range = max(lat_range, lon_range)
    lat_mid = (max(all_lats) + min(all_lats)) / 2
    lon_mid = (max(all_lons) + min(all_lons)) / 2

    plt.xlim(lon_mid - max_range / 2, lon_mid + max_range / 2)
    plt.ylim(lat_mid - max_range / 2, lat_mid + max_range / 2)

    # Labels and legend
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Coordinate Mirroring and Offset')
    plt.legend()
    plt.grid(True)
    plt.show()

# Example input
coordinates = [
    "COORD:S008.44.47.005:E115.10.34.143",
    "COORD:S008.44.46.759:E115.10.40.182",
    "COORD:S008.45.00.000:E115.10.00.000"
]
reference_coordinate = "COORD:S008.45.00.000:E115.10.00.000"
final_offset_coordinate = "COORD:S008.44.50.000:E115.10.10.000"
mirror_angle = 342  # Mirroring between South-West axis

# Convert original coordinates
original_decimal = [dms_to_decimal(coord) for coord in coordinates]

# Mirror coordinates
mirrored_decimal = mirror_coordinates(coordinates, *dms_to_decimal(reference_coordinate), mirror_angle)

# Apply offset
mirrored_offset_decimal = apply_offset(mirrored_decimal, reference_coordinate, final_offset_coordinate)

# Plot results
plot_coordinates(original_decimal, mirrored_decimal, mirrored_offset_decimal, reference_coordinate, final_offset_coordinate)

# Print in the wanted format
for coord in mirrored_offset_decimal:
    print(decimal_to_dms(coord[0], coord[1]))