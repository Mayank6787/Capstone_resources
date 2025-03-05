import json
import folium
from geopy.distance import geodesic

# Load hospital data from data.json
with open("data.json", "r") as file:
    hospital_data = json.load(file)

# Validate hospital data and extract coordinates
hospital_coords = [
    (entry["Latitude"], entry["Longitude"])
    for entry in hospital_data if "Latitude" in entry and "Longitude" in entry
]

# Check if hospital data is available
if not hospital_coords:
    raise ValueError("No valid hospital data found. Please check your data.json file.")

# Define the center of the area (adjust based on your data)
center_lat = sum(lat for lat, lon in hospital_coords) / len(hospital_coords)
center_lon = sum(lon for lat, lon in hospital_coords) / len(hospital_coords)

# Define the fixed bounding box for a 50km x 50km area
bounding_box = [
    [center_lat - 0.225, center_lon - 0.225],  # Bottom-left corner (approx. 50 km)
    [center_lat + 0.225, center_lon + 0.225],  # Top-right corner
]

# Create a Folium map with fixed boundaries
m = folium.Map(
    location=[center_lat, center_lon], 
    zoom_start=12,  # Adjust as needed
    max_bounds=True,  # Prevents panning outside the area
    control_scale=True,  # Adds a scale for reference
)

# Plot hospitals in red
for hospital in hospital_data:
    if "Latitude" in hospital and "Longitude" in hospital:
        folium.Marker(
            [hospital["Latitude"], hospital["Longitude"]],
            popup=f"{hospital['Name of Hospital']}<br>{hospital['Address']}<br>Contact: {hospital.get('Contact', 'N/A')}",
            icon=folium.Icon(color="red", icon="plus", prefix="fa")
        ).add_to(m)

# Function to get the minimum distance of a village from any hospital
def get_min_distance(village):
    return min(geodesic(village, hospital).km for hospital in hospital_coords)

# Sample village data (Replace with actual data if available)
village_coords = [(25.1, 85.1), (25.4, 85.4), (26.0, 85.9)]  # Example village coordinates

# Plot villages with color-coded markers based on distance
for lat, lon in village_coords:
    distance = get_min_distance((lat, lon))
    color = 'green' if distance < 6 else 'grey'
    
    folium.CircleMarker(
        [lat, lon], radius=6, color=color, fill=True, fill_color=color,
        popup=f"Village - {color} ({distance:.2f} km)"
    ).add_to(m)

# Restrict the map view to the 50km x 50km bounding box
m.fit_bounds(bounding_box)

# Save the map
m.save("final_map_fixed.html")
print("Map has been saved as final_map_fixed.html with a fixed 50km x 50km screen.")
