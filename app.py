import flask
import pickle
import pandas as pd
import numpy as np
import re
from flask import Flask, request, jsonify
from flask_cors import CORS # Needed to allow your website (front-end) to talk to the API

# Initialize the Flask app
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- Load Model Artifacts ---
try:
    with open('./recommendation_artifacts/ifs_recommendation_model.pkl', 'rb') as file:
        artifacts = pickle.load(file)

    model = artifacts['model']
    le = artifacts['label_encoder']
    X_cols = artifacts['feature_cols']
    all_district_cols = artifacts['all_district_cols']
    # Use a different name here to prevent shadowing the matrix inside the function
    synergy_matrix_loaded = artifacts['interaction_matrix'] 
    
    print("Model Artifacts Loaded Successfully.")

except FileNotFoundError:
    print("Error: Model file 'ifs_recommendation_model.pkl' not found. Please run the export step.")
    # Exit or handle gracefully in a real application

# --- Recommendation Function (Copied/Adapted for the API) ---
def api_recommend_ifs_combination_with_synergy(district_name, soil_ph_min, soil_ph_max, top_n=5):
    """
    Generates a synergistic recommendation list using loaded artifacts.
    """
    district_name = district_name.strip()
    district_col_name = f'District_{district_name}'
    
    # 1. Input Feature Setup & Validation
    if district_col_name not in X_cols:
        # Cannot provide full list of districts in API, so return simple error
        return {"error": f"District '{district_name}' not supported."}, 400

    input_features = {col: 0 for col in all_district_cols} 
    input_features['pH_min'] = soil_ph_min
    input_features['pH_max'] = soil_ph_max
    input_features[district_col_name] = 1

    sample_input = pd.DataFrame([input_features])
    for c in set(X_cols) - set(sample_input.columns):
        sample_input[c] = 0
    sample_input = sample_input[X_cols]

    # 2. Phase 1: Base Prediction
    proba = model.predict_proba(sample_input)[0]
    top_indices = np.argsort(proba)[-20:][::-1] # Use a fixed size for base list
    
    base_recommendations = []
    for index in top_indices:
        item_name = le.inverse_transform([index])[0]
        base_recommendations.append({
            'Item': item_name,
            'Base_Confidence': proba[index]
        })
    df_base = pd.DataFrame(base_recommendations)

    if df_base.empty:
        return {"error": "Model produced no recommendations."}, 400
    
    # 3. Phase 2: Synergy Scoring (Robust Anchor Selection)
    # We must assume the top item is the anchor since we don't have the category column (df_combined)
    # To keep the API fast, we skip the category lookup and use the highest confidence item as the anchor
    primary_crop = df_base.iloc[0]['Item']

    final_recommendations = []
    for index, row in df_base.iterrows():
        item = row['Item']
        confidence = row['Base_Confidence']
        synergy_score = 0
        
        # Check synergy in both directions
        if primary_crop in synergy_matrix_loaded and item in synergy_matrix_loaded[primary_crop]:
            synergy_score = synergy_matrix_loaded[primary_crop][item]
        elif item in synergy_matrix_loaded and primary_crop in synergy_matrix_loaded[item]:
            synergy_score = synergy_matrix_loaded[item][primary_crop]
            
        final_confidence = confidence * (1 + synergy_score)
        
        final_recommendations.append({
            'Item': item,
            'Synergy_Bonus': f"{synergy_score*100:.2f}%",
            'Final_Confidence': final_confidence
        })

    df_final = pd.DataFrame(final_recommendations).sort_values(by='Final_Confidence', ascending=False)
    
    # Format and return the top 5
    df_final['Final_Confidence'] = df_final['Final_Confidence'].apply(lambda x: f"{x*100:.2f}%")
    return df_final.head(top_n).to_dict('records'), 200


# --- API Endpoint Definition ---
@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Endpoint to receive user input and return recommendations."""
    try:
        data = request.get_json()
        
        # Validate and extract input
        district = data['district']
        ph_min = float(data['ph_min'])
        ph_max = float(data['ph_max'])
        top_n = int(data.get('top_n', 5))
        
        # Get recommendations
        recommendations, status_code = api_recommend_ifs_combination_with_synergy(district, ph_min, ph_max, top_n)
        
        if status_code != 200:
             return jsonify({"success": False, "error": recommendations['error']}), status_code

        return jsonify({"success": True, "recommendations": recommendations})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# Run the app
if __name__ == '__main__':
    # 1. Install required libraries: pip install Flask pandas numpy scikit-learn flask-cors
    # 2. Run the server: python app.py
    app.run(host='0.0.0.0', port=5000, debug=True)