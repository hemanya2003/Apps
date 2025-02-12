import pydeck as pdk
import streamlit as st

# Use your MapTiler Topo v2 URL
maptiler_url = "https://api.maptiler.com/maps/topo-v2/?key=E6ZRsLot4eQsQImxowwm"

# Create a Pydeck map with the specified MapTiler URL
deck = pdk.Deck(
    map_style=maptiler_url,  # Directly use the Topo v2 map
    initial_view_state=pdk.ViewState(
        latitude=20.5937, longitude=78.9629, zoom=4, pitch=0  # Adjust for your region
    ),
)

# Display the map in Streamlit
st.pydeck_chart(deck)
