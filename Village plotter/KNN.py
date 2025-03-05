import json
import pandas as pd
import folium
from sklearn.neighbors import KNeighborsClassifier
import numpy as np

# Load hospital data from data.json
with open("data.json", "r") as file:
    hospital_data = json.load(file)

# Extract relevant fields
hospital_coords = [(entry["Latitude"], entry["Longitude"]) for entry in hospital_data]

# Sample village data (Replace with actual data if available)
village_coords = [(25.1, 85.1), (25.4, 85.4), (26.0, 85.9)]  # Example village coordinates

# Convert to NumPy arrays
hospitals = np.array(hospital_coords)
villages = np.array(village_coords)

# Apply KNN to find nearest hospital for each village
knn = KNeighborsClassifier(n_neighbors=1)
knn.fit(hospitals, np.ones(len(hospitals)))

# Predict nearest hospital for each village and calculate distance
distances, indices = knn.kneighbors(villages)


threshold = 0.05  

# Create a Folium map
m = folium.Map(location=[25.2, 85.2], zoom_start=10)

# Plot hospitals in red
for hospital in hospital_data:
    folium.Marker(
        [hospital["Latitude"], hospital["Longitude"]],
        popup=f"{hospital['Name of Hospital']}<br>{hospital['Address']}<br>Contact: {hospital['Contact']}",
        icon=folium.Icon(color="red", icon="plus", prefix="fa")
    ).add_to(m)

# Plot villages with coloring logic
for i, (lat, lon) in enumerate(village_coords):
    color = 'green' if distances[i][0] < threshold else 'grey'
    folium.CircleMarker([lat, lon], radius=6, color=color, fill=True, fill_color=color,
                        popup=f"Village - {color}").add_to(m)

# Save the map
m.save("final_map.html")
print("Map has been saved as final_map.html")
