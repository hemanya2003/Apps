import streamlit as st
import geopandas as gpd
import pydeck as pdk

# Load your shapefile
shapefile_path = "LUSE_FINAL.shp"
gdf = gpd.read_file(shapefile_path)

# Reproject to EPSG:4326 (WGS84) if necessary
if gdf.crs != 'EPSG:4326':
    gdf = gdf.to_crs(epsg=4326)

# Explode MultiPolygon geometries into individual Polygon geometries
gdf = gdf.explode(index_parts=True).reset_index(drop=True)

# Define heights for each LANDUSE category
landuse_heights = {
    'bare': 15, 'built': 30, 'crops': 10, 'grass': 20,
    'shrub_and_scrub': 25, 'trees': 35, 'water': -5
}

# Define colors for each LANDUSE category (in RGB format)
landuse_colors = {
    'bare': [255, 192, 203], 'built': [255, 0, 0], 'crops': [255, 255, 0],
    'grass': [144, 238, 144], 'shrub_and_scrub': [255, 0, 255], 'trees': [0, 128, 0], 'water': [0, 0, 255]
}

# Assign heights and colors
gdf['height'] = gdf['LANDUSE'].map(landuse_heights)
gdf['color'] = gdf['LANDUSE'].map(landuse_colors)

# MapTiler API Key
MAPTILER_API_KEY = "E6ZRsLot4eQsQImxowwm"

# Create the PyDeck polygon layer
polygon_layer = pdk.Layer(
    'PolygonLayer',
    data=gdf,
    get_polygon='geometry.coordinates',
    extruded=True,
    get_elevation='height',
    get_fill_color='color',
    elevation_scale=1,
    pickable=True,
)

# Tile Layers
tile_layer_satellite = pdk.Layer(
    'TileLayer',
    data=None,
    get_tile_data=f'https://api.maptiler.com/maps/satellite/{{z}}/{{x}}/{{y}}.jpg?key={MAPTILER_API_KEY}',
    pickable=False,
    tile_size=256,
)

tile_layer_topo = pdk.Layer(
    'TileLayer',
    data=None,
    get_tile_data=f'https://api.maptiler.com/maps/topo-v2/{{z}}/{{x}}/{{y}}.png?key={MAPTILER_API_KEY}',
    pickable=False,
    tile_size=256,
)

# Set the view state to center on the data
view_state = pdk.ViewState(
    latitude=gdf.geometry.centroid.y.mean(),
    longitude=gdf.geometry.centroid.x.mean(),
    zoom=10,
    pitch=45,
    bearing=30,
)

# Streamlit App
st.title("Interactive Land Use Visualization with Layer Controls")

# Base map and style selection
base_map = st.selectbox("Select Base Map", ["Satellite", "Topo v2"])
map_style = st.selectbox("Select Map Style", ["Hybrid", "Streets", "Outdoor",Topo Map”])

# MapTiler styles
map_styles = {
    "Hybrid": f"https://api.maptiler.com/maps/hybrid/style.json?key={MAPTILER_API_KEY}",
    "Streets": f"https://api.maptiler.com/maps/streets/style.json?key={MAPTILER_API_KEY}",
    "Outdoor": f"https://api.maptiler.com/maps/outdoor/style.json?key={MAPTILER_API_KEY}",

 "Topo Map": f"https://api.maptiler.com/maps/topo-v2/style.json?key={MAPTILER_API_KEY}",
}


}

# Select base layer
tile_layer = tile_layer_satellite if base_map == "Satellite" else tile_layer_topo

# Toggle Land Use Polygons
show_landuse = st.checkbox("Show Land Use Polygons", value=True)

# Create PyDeck map
deck = pdk.Deck(
    layers=[tile_layer, polygon_layer] if show_landuse else [tile_layer],
    initial_view_state=view_state,
    map_style=map_styles[map_style],  # Apply selected style
)

# Display the map
st.pydeck_chart(deck)
