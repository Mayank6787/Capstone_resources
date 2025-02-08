import folium
import pandas as pd

# Load the JSON file
data = pd.read_json('data.json')

# Create a map centered at the average location
map_center = [data['Latitude'].mean(), data['Longitude'].mean()]
hospital_map = folium.Map(location=map_center, zoom_start=12)

# Add hospital locations to the map
for _, row in data.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"Hospital: {row['Name of Hospital']}"  # Assuming 'name' column exists
    ).add_to(hospital_map)

# Save the map to an HTML file
hospital_map.save('hospital_map.html')

print("Map has been created and saved as 'hospital_map.html'")
