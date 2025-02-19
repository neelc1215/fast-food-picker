from flask import Flask, render_template, request
import requests
import random
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Sample menu database (for chain restaurants)
menu_database = {
    "McDonald's": ["Big Mac", "McChicken", "Filet-O-Fish"],
    "Burger King": ["Whopper", "Chicken Fries", "Bacon King"],
    "Taco Bell": ["Crunchwrap Supreme", "Quesarito", "Doritos Locos Tacos"],
    "Chick-fil-A": ["Chicken Sandwich", "Nuggets", "Spicy Deluxe Sandwich"],
    "Wendy's": ["Baconator", "Spicy Nuggets", "Frosty"],
    "Subway": ["Italian BMT", "Turkey Breast Sandwich", "Meatball Marinara"],
    "Chipotle": ["Burrito Bowl", "Chicken Burrito", "Steak Tacos"],
    "Panda Express": ["Orange Chicken", "Kung Pao Chicken", "Beijing Beef"]
}

# Cuisine options mapped to Overpass API tags
cuisine_options = {
    "Mexican": "mexican",
    "American": "burger|american",
    "Chinese": "chinese",
    "Any": None
}

def get_coordinates(zip_code):
    """Convert ZIP code to latitude and longitude using OpenStreetMap's Nominatim API."""
    geolocator = Nominatim(user_agent="meal_picker")
    location = geolocator.geocode(zip_code)
    return (location.latitude, location.longitude) if location else None

def get_restaurants(lat, lon, radius=10000, cuisine=None):
    """Fetch restaurants within a given radius using Overpass API and filter by cuisine."""
    cuisine_filter = f'["cuisine"~"{cuisine}"]' if cuisine else ""
    url = f"https://overpass-api.de/api/interpreter?data=[out:json];node['amenity'='restaurant']{cuisine_filter}(around:{radius},{lat},{lon});out;"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        restaurants = [element["tags"]["name"] for element in data["elements"] if "tags" in element and "name" in element["tags"]]
        return restaurants
    return None

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        zip_code = request.form.get("zip_code")
        cuisine_selected = request.form.get("cuisine")
        cuisine_filter = cuisine_options.get(cuisine_selected, None)

        coordinates = get_coordinates(zip_code)
        if coordinates:
            lat, lon = coordinates
            restaurants = get_restaurants(lat, lon, cuisine=cuisine_filter)

            if restaurants:
                restaurants_with_menu = [r for r in restaurants if r in menu_database]
                restaurants_without_menu = [r for r in restaurants if r not in menu_database]

                if restaurants_with_menu:
                    selected_restaurant = random.choice(restaurants_with_menu)
                    recommended_item = random.choice(menu_database[selected_restaurant])
                    return render_template("index.html", restaurant=selected_restaurant, item=recommended_item)

                elif restaurants_without_menu:
                    selected_restaurant = random.choice(restaurants_without_menu)
                    return render_template("index.html", restaurant=selected_restaurant, item=None)
            return render_template("index.html", error="No restaurants found. Try a different input.")
        return render_template("index.html", error="Invalid ZIP code. Try again.")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
