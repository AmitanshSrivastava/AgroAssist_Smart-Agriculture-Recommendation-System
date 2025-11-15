from flask import Flask, render_template, request
import pickle
import requests
import pandas as pd

app = Flask(__name__)

# -----------------------------
# Load datasets globally
# -----------------------------
trees_df = pd.read_csv("datasets/Commercial_trees_UttarPradesh.csv")
crops_df = pd.read_csv("datasets/Field_Crop_UttarPradesh.csv")
flowers_df = pd.read_csv("datasets/flori.csv")

# -----------------------------
# Load trained model if required (currently optional)
# -----------------------------
# model = pickle.load(open("IFS_model.pkl", "rb"))

# -----------------------------
# Open-Meteo API Configuration
# -----------------------------
def get_weather(district):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={district}&count=1&language=en&format=json"
        geo_data = requests.get(geo_url).json()

        if "results" not in geo_data or len(geo_data["results"]) == 0:
            return {"temp": "N/A", "humidity": "N/A", "description": "Not Found"}

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        data = requests.get(weather_url).json()
        temp = data["current_weather"]["temperature"]
        description = data["current_weather"]["weathercode"]

        return {"temp": temp, "humidity": "N/A", "description": f"Weather Code: {description}"}
    except:
        return {"temp": "N/A", "humidity": "N/A", "description": "Not Found"}

# -----------------------------
# Recommendation function
# -----------------------------
def get_recommendation(district, soil):
    # Tree selection
    tree_row = trees_df[trees_df.iloc[:, 0] == district]
    tree = tree_row.sample(1).iloc[0,1].split('—')[0].strip() if not tree_row.empty else "Unknown"

    # Crop selection
    crop_row = crops_df[(crops_df.iloc[:,0] == district) & (crops_df.iloc[:,2].str.contains(soil, case=False, na=False))]
    if not crop_row.empty:
        crop = crop_row.sample(1).iloc[0,1].strip()
    else:
        fallback = crops_df[crops_df.iloc[:,0] == district]
        crop = fallback.sample(1).iloc[0,1].strip() if not fallback.empty else "Unknown"

    # Flower selection
    flower_row = flowers_df[flowers_df.iloc[:,0] == district]
    if not flower_row.empty:
        flowers_list = flower_row.iloc[0,1].split(',')
        flower = flowers_list[0].strip()  # pick first flower
    else:
        flower = "Unknown"

    return {"tree": tree, "crop": crop, "flower": flower}

# -----------------------------
# Home page
# -----------------------------
@app.route('/')
def home():
    # Combine all districts from the three datasets
    districts = pd.concat([
        trees_df.iloc[:,0],
        crops_df.iloc[:,0],
        flowers_df.iloc[:,0]
    ]).dropna().unique()
    districts = sorted(districts)
    return render_template("index.html", districts=districts)

# -----------------------------
# Prediction route
# -----------------------------
@app.route('/predict', methods=['POST'])
def predict():
    district = request.form['district']
    soil = request.form.get('soil', 'loamy')
    lang = request.form.get('language', 'english')
    try:
        land_area = float(request.form.get('area', 1.0))
    except ValueError:
        land_area = 1.0

    # Weather info
    weather = get_weather(district)

    # Get recommendation
    rec = get_recommendation(district, soil)

    # Allocation percentages
    tree_pct, flower_pct, crop_pct = 0.2, 0.3, 0.5
    allocation = {
        "trees": f"{tree_pct * land_area:.2f} hectares ({int(tree_pct*100)}%)",
        "flowers": f"{flower_pct * land_area:.2f} hectares ({int(flower_pct*100)}%)",
        "crops": f"{crop_pct * land_area:.2f} hectares ({int(crop_pct*100)}%)",
        "layout": "Plant trees on the borders and flowers/crops in the middle"
    }

    # Hindi translations
    if lang.lower() in ['hi', 'hindi']:
        translation = {"tree": "पेड़", "crop": "फसल", "flower": "फूल", "recommended": "एकीकृत खेती प्रणाली की अनुशंसा"}
        allocation = {
            "trees": f"{tree_pct * land_area:.2f} हेक्टेयर ({int(tree_pct*100)}%) पर पेड़",
            "flowers": f"{flower_pct * land_area:.2f} हेक्टेयर ({int(flower_pct*100)}%) पर फूल",
            "crops": f"{crop_pct * land_area:.2f} हेक्टेयर ({int(crop_pct*100)}%) पर फसल",
            "layout": "सीमाओं पर पेड़ और बीच में फूल/फसल लगाएँ"
        }
    else:
        translation = {"tree": "Tree", "crop": "Crop", "flower": "Flower", "recommended": "Integrated Farming System Recommendation"}

    return render_template("result.html",
                           district=district,
                           weather=weather,
                           rec=rec,
                           soil=soil,
                           land_area=land_area,
                           translation=translation,
                           lang=lang,
                           allocation=allocation)

# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
