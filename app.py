import streamlit as st
import pandas as pd
import re
from datetime import datetime
import time

# --- 1. Constants and Configuration ---

# UI Color Palette (Sage Green / Soft Gold Theme)
COLOR_PRIMARY_GREEN = '#769077'  # Muted Sage Green
COLOR_SECONDARY_GOLD = '#E6B34A'  # Soft Gold Accent
COLOR_ACCENT_BLUE = '#4A8BE6'    # Navy Blue/Steel Blue for Trees/Wind
COLOR_ACCENT_PINK = '#E64A8B'    # Deep Pink for Flowers
COLOR_TEXT_MAIN = '#FFFFFF'       # White text for all content

# Background Image URLs
HOME_PAGE_BACKGROUND_URL = "https://images.pexels.com/photos/34768351/pexels-photo-34768351.jpeg" 
REC_PAGE_BACKGROUND_URL = "https://images.pexels.com/photos/7944397/pexels-photo-7944397.jpeg"

# --- Complete List of 75 Districts of Uttar Pradesh ---
DISTRICTS = [
    "Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya", "Ayodhya", 
    "Azamgarh", "Badaun", "Baghpat", "Bahraich", "Balarampur", "Banda", "Barabanki", 
    "Bareilly", "Basti", "Bhadohi", "Bijnor", "Bulandshahr", "Chandauli", "Chitrakoot", 
    "Deoria", "Etah", "Etawah", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar (Noida)", 
    "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur", "Hapur", "Hardoi", 
    "Hathras", "Jalaun", "Jaunpur", "Jhansi", "Kannauj", "Kanpur Dehat", "Kanpur Nagar", 
    "Kasganh", "Kaushambi", "Kheri", "Kushinagar", "Lalitpur", "Lucknow", "Maharajganh", 
    "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad", 
    "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj", "Rae Bareli", "Rampur", 
    "Saharanpur", "Sambhal", "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shravasti", 
    "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"
]

ROI_MAP = {
    "Poplar": "High (5-7 years)", "Teak": "Very High (15+ years)", 
    "Mahogany": "High (10-12 years)", "Mango": "Medium (8-10 years)", 
    "Amla": "Medium (3-5 years)"
}
COMPLEMENTARY_INTERACTIONS = {
    "Mango": ["Turmeric"], "Wheat": ["Marigold"], "Rice": ["Fish Farming"]
}

# Mock DataFrames
df_field_crop = pd.DataFrame({
    'District': ['Lucknow', 'Lucknow', 'Lucknow', 'Varanasi', 'Varanasi', 'Meerut', 'Agra', 'Prayagraj', 'Kanpur Nagar', 'Bareilly'],
    'Season': ['Kharif', 'Rabi', 'Kharif', 'Kharif', 'Rabi', 'Rabi', 'Kharif', 'Rabi', 'Kharif', 'Rabi'],
    'Crop': ['Rice', 'Wheat', 'Maize', 'Rice', 'Lentil', 'Sugarcane', 'Bajra', 'Mustard', 'Soybean', 'Barley'],
    'Soil_Water_pH': ['Alluvial, pH 6.0-7.5, High Water', 'Loamy, pH 6.0-7.0, Medium Water', 'Sandy/Loamy, pH 5.5-7.0, Medium Water', 'Clay, pH 6.0-8.0, High Water', 'Loamy, pH 6.0-8.0, Low Water', 'Clay Loam, pH 6.5-8.0, High Water', 'Sandy, pH 6.0-7.5, Low Water', 'Loamy, pH 6.0-7.0, Low Water', 'Clay Loam, pH 6.5-7.5, Medium Water', 'Sandy Loam, pH 6.0-7.5, Medium Water']
})
df_commercial_trees = pd.DataFrame({
    'District': ['Lucknow', 'Varanasi', 'Agra', 'Kanpur Nagar', 'Prayagraj', 'Gautam Buddha Nagar (Noida)', 'Gorakhpur', 'Ayodhya'],
    'Tree': ['Poplar', 'Teak', 'Mahogany', 'Mango', 'Amla', 'Eucalyptus', 'Sheesham', 'Sandalwood'],
    'Soil_Water_pH': ['Loamy/Clay, Well-drained', 'Sandy/Loamy, pH 6.5-7.5', 'Alluvial, Good drainage', 'Loamy, Moderate water', 'Loamy, Well-drained', 'Well-drained, Low pH', 'Alluvial, Moderate Water', 'Sandy Loam, Well-drained']
})
df_flori = pd.DataFrame({
    'District': ['Lucknow', 'Varanasi', 'Kanpur Nagar', 'Agra', 'Aligarh', 'Bareilly', 'Ghaziabad', 'Meerut'],
    'Flower': ['Marigold, Rose', 'Tuberose, Gladiolus', 'Marigold, Jasmine', 'Rose, Marigold', 'Chrysanthemum', 'Calendula', 'Rose', 'Gladiolus'],
    'Soil_Water_pH': ['Sandy Loam, pH 6.0-7.5', 'Loamy, Moderate water', 'Alluvial, Well-drained', 'Loamy/Clay, pH 6.5-7.5', 'Sandy Loam, pH 6.0-7.0', 'Clay Loam, pH 6.5-7.5', 'Sandy Loam, pH 6.0-7.5', 'Loamy, Moderate Water']
})

# Dictionary for bilingual text strings
BILINGUAL_STRINGS = {
    'title': {'en': "Agro-Assist: Integrated Farming System Advisor", 'hi': "एग्रो-असिस्ट: एकीकृत कृषि प्रणाली सलाहकार"},
    'subtitle': {'en': "Smart Recommendations for Uttar Pradesh Agriculture", 'hi': "उत्तर प्रदेश की कृषि के लिए स्मार्ट सिफारिशें"},
    'about_us_heading': {'en': "About Agro-Assist", 'hi': "एग्रो-असिस्ट के बारे में"},
    'about_us_text': {'en': "Agro-Assist is an AI-powered tool designed to help farmers in Uttar Pradesh optimize their land use. By combining **local data**, **predictive modeling** for field crops, and **weather information**, we provide integrated recommendations.", 'hi': "एग्रो-असिस्ट उत्तर प्रदेश के किसानों को उनकी भूमि के उपयोग को अनुकूलित करने में मदद करने के लिए डिज़ाइन किया गया एक AI-संचालित उपकरण है। **स्थानीय डेटा**, **पूर्वानुमानित मॉडलिंग** और **मौसम की जानकारी** को मिलाकर, हम एकीकृत सिफारिशें प्रदान करते हैं।"},
    'ifs_heading': {'en': "Integrated Farming System (IFS)", 'hi': "एकीकृत कृषि प्रणाली (IFS)"},
    'ifs_text': {'en': "Our focus is on the Integrated Farming System, which combines multiple components like crops, trees, and livestock to maximize resource utilization and return on investment while minimizing waste. It’s the sustainable future of farming.", 'hi': "हमारा ध्यान एकीकृत कृषि प्रणाली पर है, जो संसाधनों के उपयोग और निवेश पर रिटर्न को अधिकतम करने के लिए फसलों, पेड़ों और पशुधन जैसे कई घटकों को जोड़ती है, जिससे अपशिष्ट कम होता है। यह खेती का टिकाऊ भविष्य है।"},
    
    # NEW HOME PAGE KVK STRINGS
    'home_kvk_heading': {'en': "Partnering with Krishi Vigyan Kendras (KVKs)", 'hi': "कृषि विज्ञान केंद्रों (KVKs) के साथ साझेदारी"},
    'home_kvk_text': {'en': "Our recommendations are validated and supported by the **local expertise** of Krishi Vigyan Kendras (KVKs). We bridge the gap between AI insights and on-ground practical agricultural guidance by incorporating feedback on regional soil variations and climate-resilient farming techniques. This ensures our advice is scientifically advanced and locally relevant.", 'hi': "हमारी सिफारिशें कृषि विज्ञान केंद्रों (KVKs) की **स्थानीय विशेषज्ञता** द्वारा मान्य और समर्थित हैं। हम क्षेत्रीय मिट्टी के बदलाव और जलवायु-लचीली खेती की तकनीकों पर प्रतिक्रिया को शामिल करके AI अंतर्दृष्टि और जमीनी स्तर पर व्यावहारिक कृषि मार्गदर्शन के बीच सेतु का काम करते हैं। यह सुनिश्चित करता है कि हमारी सलाह वैज्ञानिक रूप से उन्नत और स्थानीय रूप से प्रासंगिक है।"},
    
    # --- NEW ECONOMIC IMPACT STRINGS ---
    'eco_heading': {'en': "Economic Impact of Integrated Farming", 'hi': "एकीकृत खेती का आर्थिक प्रभाव"},
    'eco_point1_title': {'en': "Increased Profitability", 'hi': "बढ़ी हुई लाभप्रदता"},
    'eco_point1_text': {'en': "Diversification minimizes risk and opens up multiple revenue streams (e.g., selling wood, fruits, and flowers).", 'hi': "विविधीकरण जोखिम को कम करता है और कई राजस्व स्रोत खोलता है (जैसे लकड़ी, फल और फूल बेचना)।"},
    'eco_point2_title': {'en': "Resource Efficiency", 'hi': "संसाधन दक्षता"},
    'eco_point2_text': {'en': "Waste from one component (e.g., crop residue) becomes input for another (e.g., livestock feed), reducing operational costs.", 'hi': "एक घटक का अपशिष्ट (जैसे फसल अवशेष) दूसरे के लिए इनपुट बन जाता है (जैसे पशुधन चारा), जिससे परिचालन लागत कम हो जाती है।"},
    'eco_point3_title': {'en': "Long-Term Wealth", 'hi': "दीर्घकालिक धन"},
    'eco_point3_text': {'en': "Commercial tree components provide significant, high-value returns after 5-15 years, acting as a retirement fund.", 'hi': "व्यावसायिक पेड़ घटक 5-15 वर्षों के बाद महत्वपूर्ण, उच्च मूल्य रिटर्न प्रदान करते हैं, जो एक सेवानिवृत्ति निधि के रूप में कार्य करते हैं।"},
    # --- END NEW STRINGS ---

    'get_rec_button': {'en': "Get Your Custom Farm Recommendations", 'hi': "अपनी कस्टम कृषि सिफारिशें प्राप्त करें"},
    'back_button': {'en': "Back to Home", 'hi': "होम पर वापस"},
    'input_title': {'en': "Farm Recommendation System", 'hi': "कृषि सिफारिश प्रणाली"},
    'input_prompt': {'en': "Please enter your location details and requirements below:", 'hi': "कृपया नीचे अपनी स्थान संबंधी जानकारी और आवश्यकताएँ दर्ज करें:"},
    'select_district': {'en': "Select District", 'hi': "जिला चुनें"},
    'select_soil': {'en': "Select Soil Type", 'hi': "मिट्टी का प्रकार चुनें"},
    'select_season': {'en': "Select Crop Season", 'hi': "फसल का मौसम चुनें"},
    'generate_button': {'en': "Generate Recommendations", 'hi': "सिफारिशें उत्पन्न करें"},
    
    # Weather Strings
    'weather_heading': {'en': "Current Weather in", 'hi': "वर्तमान मौसम"},
    'temp': {'en': "Temperature", 'hi': "तापमान"},
    'wind': {'en': "Wind Speed", 'hi': "हवा की गति"},
    'time': {'en': "Time (Local)", 'hi': "समय (स्थानीय)"},
    'daily_forecast': {'en': "7-Day Forecast", 'hi': "7 दिन का पूर्वानुमान"},
    'date_col': {'en': "Date", 'hi': "तिथि"},
    'max_temp_col': {'en': "Max (°C)", 'hi': "अधिकतम (°C)"},
    'min_temp_col': {'en': "Min (°C)", 'hi': "न्यूनतम (°C)"},
    'rain_col': {'en': "Rain (mm)", 'hi': "वर्षा (मिमी)"},

    # Recommendation Strings
    'rec_heading': {'en': "Your Integrated Farming Recommendations", 'hi': "आपकी एकीकृत कृषि सिफारिशें"},
    'tab_crops': {'en': "Field Crops", 'hi': "खेत की फसलें"},
    'tab_trees': {'en': "Commercial Trees", 'hi': "व्यावसायिक पेड़"},
    'tab_flowers': {'en': "Flowers", 'hi': "फूल"},
    'tab_ifs': {'en': "IFS Strategy", 'hi': "IFS रणनीति"},
    'crop_rec_subheader': {'en': "Top crops for {} season in {} soil:", 'hi': "{} मिट्टी में {} मौसम के लिए शीर्ष फसलें:"},
    'tree_rec_subheader': {'en': "Top commercial trees suitable for {} soil:", 'hi': "{} मिट्टी के लिए उपयुक्त शीर्ष व्यावसायिक पेड़:"},
    'flower_rec_subheader': {'en': "Top flowers for {} soil:", 'hi': "{} मिट्टी के लिए शीर्ष फूल:"},
    'req': {'en': "Requirement:", 'hi': "आवश्यकता:"},
    'roi': {'en': "ROI/Return Period:", 'hi': "ROI/रिटर्न अवधि:"},
    'no_match': {'en': "No highly specific crop matches found. Displaying general regional suggestions.", 'hi': "कोई उच्च विशिष्ट फसल मेल नहीं मिला। सामान्य क्षेत्रीय सुझाव प्रदर्शित किए जा रहे हैं।"},
    'no_tree_match': {'en': "No specific tree matches found. Displaying general regional suggestions.", 'hi': "कोई विशिष्ट पेड़ मेल नहीं मिला। सामान्य क्षेत्रीय सुझाव प्रदर्शित किए जा रहे हैं।"},
    'no_flower_match': {'en': "No specific flower matches found. Displaying general regional suggestions.", 'hi': "कोई विशिष्ट फूल मेल नहीं मिला। सामान्य क्षेत्रीय सुझाव प्रदर्शित किए जा रहे हैं।"},
    
    # IFS Tab Strings
    'interaction_title': {'en': "Synergy Check: Direct Interactions", 'hi': "तालमेल जाँच: सीधा इंटरैक्शन"},
    'interaction_desc': {'en': "Integrated Farming relies on synergistic relationships. We check for complementary interactions based on traditional knowledge and scientific principles (e.g., flowers acting as pest repellents for crops).", 'hi': "एकीकृत खेती सहक्रियात्मक संबंधों पर निर्भर करती है। हम पारंपरिक ज्ञान और वैज्ञानिक सिद्धांतों के आधार पर पूरक इंटरैक्शन की जाँच करते हैं (उदाहरण के लिए, फसल कीटों के लिए विकर्षक के रूप में कार्य करने वाले फूल)।"},
    
    # Navigation Strings
    'nav_home': {'en': "Home", 'hi': "होम"},
    'nav_about': {'en': "About Agro-Assist", 'hi': "एग्रो-असिस्ट के बारे में"},
    'nav_collaboration': {'en': "KVK Collaboration", 'hi': "कृषि विज्ञान केंद्र सहयोग"},

    # About Page Strings
    'about_page_heading': {'en': "Our Vision for Smart Agriculture", 'hi': "स्मार्ट कृषि के लिए हमारा दृष्टिकोण"},
    'about_page_text1': {'en': "Agro-Assist utilizes a rule-based engine powered by local soil and climate data combined with machine learning models trained on historical yield data from various districts in Uttar Pradesh.", 'hi': "एग्रो-असिस्ट उत्तर प्रदेश के विभिन्न जिलों से ऐतिहासिक उपज डेटा पर प्रशिक्षित मशीन लर्निंग मॉडल के साथ संयुक्त स्थानीय मिट्टी और जलवायु डेटा द्वारा संचालित एक नियम-आधारित इंजन का उपयोग करता है।"},
    'about_page_text2': {'en': "Our goal is to provide accessible, location-specific, and profitable farming advice, promoting climate resilience and sustainable practices across the state.", 'hi': "हमारा लक्ष्य सुलभ, स्थान-विशिष्ट और लाभदायक कृषि सलाह प्रदान करना है, जो पूरे राज्य में जलवायु लचीलापन और टिकाऊ प्रथाओं को बढ़ावा दे।"},

    # Collaboration Page Strings
    'collaboration_page_heading': {'en': "Collaborating with Krishi Vigyan Kendras (KVKs)", 'hi': "कृषि विज्ञान केंद्रों (KVKs) के साथ सहयोग"},
    'collaboration_page_text_main': {'en': "KVKs are the backbone of agricultural extension in India. Our digital recommendations are designed to work hand-in-hand with the on-ground expertise of KVKs. Always validate high-investment decisions with your local KVK for the best results.", 'hi': "KVKs भारत में कृषि विस्तार की रीढ़ हैं। हमारी डिजिटल सिफारिशें KVKs की ऑन-ग्राउंड विशेषज्ञता के साथ मिलकर काम करने के लिए डिज़ाइन की गई हैं। सर्वोत्तम परिणामों के लिए हमेशा अपने स्थानीय KVK के साथ उच्च-निवेश के फैसलों को मान्य करें।"},
    'collaboration_kvk_important': {'en': "Why KVKs are Important:", 'hi': "KVKs क्यों महत्वपूर्ण हैं:"},
    'collaboration_page_list1': {'en': "Local Expertise: KVKs possess site-specific knowledge crucial for verifying AI recommendations.", 'hi': "स्थानीय विशेषज्ञता: KVKs के पास AI सिफारिशों को सत्यापित करने के लिए महत्वपूर्ण स्थल-विशिष्ट ज्ञान होता है।"},
    'collaboration_page_list2': {'en': "Training & Extension: They provide practical training and demonstration services to farmers.", 'hi': "प्रशिक्षण और विस्तार: वे किसानों को व्यावहारिक प्रशिक्षण और प्रदर्शन सेवाएं प्रदान करते हैं।"},
    'collaboration_page_list3': {'en': "Technology Dissemination: They ensure new, optimized farming techniques reach the grassroots level.", 'hi': "प्रौद्योगिकी प्रसार: वे सुनिश्चित करते हैं कि नई, अनुकूलित खेती की तकनीकें जमीनी स्तर तक पहुंचें।"},
}

def get_string(key, lang):
    """Retrieves the bilingual string."""
    return BILINGUAL_STRINGS.get(key, {}).get(lang, key)

# --- 2. Mock API/Data Fetching Functions (Simplified/Removed Unused) ---

def get_lat_lon(district):
    """Mock function to return Lat/Lon for a district."""
    coords = {
        "Lucknow": (26.8467, 80.9462), "Varanasi": (25.3176, 82.9739),
        "Kanpur Nagar": (26.4499, 80.3319), "Agra": (27.1767, 78.0081),
        "Prayagraj": (25.4358, 81.8463), "Gautam Buddha Nagar (Noida)": (28.5355, 77.3910)
    }
    return coords.get(district, (26.8467, 80.9462)) # Default to Lucknow

def get_weather_data(lat, lon):
    """Mock function to fetch simplified weather data."""
    time.sleep(0.5) 
    current_time = datetime.now().isoformat()
    return {
        'current_weather': {
            'temperature': 28.5, 'windspeed': 15.2, 'time': current_time
        },
        'daily': {
            'time': [
                (datetime.now() + pd.Timedelta(days=i)).isoformat() for i in range(1, 8)
            ],
            'temperature_2m_max': [30, 31, 29, 32, 30, 29, 31],
            'temperature_2m_min': [18, 19, 17, 20, 18, 17, 19],
            'precipitation_sum': [0.0, 0.5, 0.0, 1.2, 0.0, 0.0, 0.8]
        }
    }

# --- 3. Recommendation Logic Functions (MOCK) ---
def get_recommendations(district, soil_type_input, crop_season):
    """
    Combines rule-based logic to suggest crops, trees, and flowers.
    """
    season_en = 'Kharif' if crop_season in ['खरीफ', 'Kharif'] else 'Rabi'
    soil_keyword = soil_type_input.split()[0].replace('मिट्टी', '').replace('Soil', '').strip()
    soil_match = lambda req: bool(re.search(soil_keyword, req, re.IGNORECASE))
    
    # --- Crops ---
    district_season_crops = df_field_crop[
        (df_field_crop['District'] == district) & 
        (df_field_crop['Season'] == season_en) 
    ].copy()
    recommended_crops_df = district_season_crops[
        district_season_crops['Soil_Water_pH'].astype(str).apply(soil_match)
    ].copy()
    if recommended_crops_df.empty:
        recommended_crops_df = district_season_crops
        if recommended_crops_df.empty:
            recommended_crops_df = df_field_crop[df_field_crop['Season'] == season_en].copy() # Fallback to any crop in season
    recommended_crops = recommended_crops_df['Crop'].unique().tolist()[:3]
        
    # --- Trees ---
    district_trees = df_commercial_trees[df_commercial_trees['District'] == district].copy()
    recommended_trees_df = district_trees[
        district_trees['Soil_Water_pH'].astype(str).apply(soil_match)
    ].copy()
    if recommended_trees_df.empty:
        if not district_trees.empty:
            recommended_trees_df = district_trees.copy()
        else:
            recommended_trees_df = df_commercial_trees.copy() # Absolute fallback
    recommended_trees = recommended_trees_df['Tree'].unique().tolist()[:3]

    # --- Flowers ---
    district_flori = df_flori[df_flori['District'] == district].copy()
    recommended_flowers_df = district_flori[
        district_flori['Soil_Water_pH'].astype(str).apply(soil_match) # Fixed: Match soil on soil column
    ].copy()
    if recommended_flowers_df.empty:
        if not district_flori.empty:
            recommended_flowers_df = district_flori.copy()
        else:
            recommended_flowers_df = df_flori.copy()
            
    recommended_flowers_raw = recommended_flowers_df['Flower'].str.split(', ').explode().str.strip().unique().tolist()
    recommended_flowers = list(set(recommended_flowers_raw))[:3]
    
    return recommended_crops, recommended_trees, recommended_flowers

# --- 7. Streamlit App Layout Functions ---

def display_recommendation_card(title, requirement, color_code, roi=None):
    """
    Generates a styled Markdown card for a recommendation item.
    Cards are now semi-transparent.
    """
    lang = st.session_state.lang
    roi_html = (
        f'<p style="margin: 0; font-size: 1.1em; padding-top: 5px;">'
        f'<span style="font-weight: bold; color: {color_code};"> {get_string("roi", lang)}</span> {roi}'
        f'</p>'
    ) if roi else ''
    
    content = f"""
    <div class="rec-item-card" style="border-left: 8px solid {color_code};">
        <h4 style="color: {COLOR_TEXT_MAIN} !important; margin-bottom: 8px; font-weight: 800; font-size: 1.5em;">{title}</h4>
        <p style="margin: 0; font-size: 1.1em;">
            <span style="font-weight: bold; color: {color_code};"> {get_string('req', lang)}</span> {requirement}
        </p>
        {roi_html}
    </div>
    """
    st.markdown(content, unsafe_allow_html=True)

def inject_page_css(page, home_bg, rec_bg):
    """
    Injects global CSS with dynamic background and "glassmorphism" UI.
    Applies 'DM Serif Text' only to h1 headings.
    """
    bg_url = rec_bg if page == 'recommendation' else home_bg

    # 1. Inject Google Font Link (Updated to include DM Serif Text ONLY)
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Text:ital@0;1&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # 2. Inject Custom Styles
    st.markdown(f"""
    <style>
    /* Global Styles */
    .stApp {{
        background-color: #f8f9fa;
        color: {COLOR_TEXT_MAIN}; 
        background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), url('{bg_url}'); 
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    }}
    
    /* --- HEADING STYLING --- */
    /* H1 uses DM Serif Text (Serif/Classic) */
    .stApp h1 {{
        color: {COLOR_TEXT_MAIN} !important; 
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
        font-family: "DM Serif Text", serif !important; 
        font-weight: 400; /* Use regular weight as specified */
    }}
    /* H2 to H6 use a readable, simple font (like the original intent) */
    .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
        color: {COLOR_TEXT_MAIN} !important; 
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
    }}
    
    /* Keep body text as default sans-serif for readability */
    .stApp p, .stApp li, .stMarkdown p, .stForm label,
    .stSelectbox label, .stTabs [data-baseweb="tab-list"] button p,
    .stDataFrame th, .stDataFrame td, .stAlert p {{
        color: {COLOR_TEXT_MAIN} !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
    }}

    /* Main Content Box: REMOVED solid white, now just a container */
    .main > div {{
        background: none; /* Remove the solid white background */
        padding: 20px;
    }}
    
    /* --- "Glass" Card Styling --- */
    .card-base {{
        background-color: rgba(0, 0, 0, 0.4); /* Semi-transparent dark card */
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3); 
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2); /* Light border for glass effect */
    }}
    .rec-item-card {{
        background-color: rgba(255, 255, 255, 0.1); /* Lighter glass for recs */
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    /* Specific coloring for card headers (which are h2/h3) */
    .home-card-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }}
    .home-card-header h2 {{
        margin: 0;
        font-size: 1.8em !important;
        color: {COLOR_SECONDARY_GOLD} !important; /* Gold header for home cards */
        text-shadow: none; /* Remove shadow on specific color elements */
    }}
    .icon-large {{
        font-size: 2em;
        line-height: 1;
        color: {COLOR_SECONDARY_GOLD};
    }}
    
    /* Recommendation Form Styling (Select Boxes) */
    .stSelectbox > div, .stTextInput > div > input {{
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 8px;
    }}
    .stSelectbox svg {{ /* Dropdown arrow */
        fill: white !important;
    }}
    
    /* Recommendation Tabs */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {{
        color: {COLOR_SECONDARY_GOLD} !important;
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important; /* Keep tab text readable */
    }}
    .stTabs [data-baseweb="tab-list"] {{
        border-bottom-color: rgba(255, 255, 255, 0.3) !important;
    }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        border-bottom-color: {COLOR_SECONDARY_GOLD} !important;
    }}
    
    /* Dataframe Styling (for weather) */
    .stDataFrame {{
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 8px;
    }}
    .stDataFrame header {{ /* Header row */
        background-color: rgba(0, 0, 0, 0.4);
    }}

    /* Sidebar Styling (Remains solid color) */
    .stSidebar > div:first-child {{
        background-color: {COLOR_PRIMARY_GREEN};
        background-image: none;
        padding-top: 20px;
        color: white; 
    }}
    .sidebar-heading {{
        color: {COLOR_SECONDARY_GOLD};
        font-weight: bold;
        padding: 0 10px 10px;
        border-bottom: 2px solid {COLOR_SECONDARY_GOLD};
        margin-bottom: 15px;
        font-size: 1.2em;
    }}
    .stRadio div[role="radiogroup"] label {{
        color: white !important;
        font-size: 1.1em;
        padding: 8px 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        transition: background-color 0.2s;
        border: 1px solid rgba(255, 255, 255, 0.2); 
    }}
    .stRadio div[role="radiogroup"] label:has(input:checked) {{
        background-color: {COLOR_SECONDARY_GOLD} !important;
        color: {COLOR_TEXT_MAIN} !important; /* Text inside selected is dark */
        text-shadow: none !important;
    }}
    .stRadio div[role="radiogroup"] label:hover {{
        background-color: #8fa691; 
    }}
    
    /* Button Styling */
    .stButton>button {{
        background-color: {COLOR_SECONDARY_GOLD};
        color: {COLOR_TEXT_MAIN}; /* Dark text on gold button */
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        border: none;
        transition: background-color 0.2s;
        text-shadow: none !important;
    }}
    .stButton>button:hover {{
        background-color: #ffdb58; /* Lighter gold */
    }}
    
    /* Economic Feature Cards */
    .eco-feature-card {{
        padding: 20px;
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        min-height: 150px;
        display: flex;
        flex-direction: column;
    }}
    .eco-feature-card h3 {{
        color: {COLOR_PRIMARY_GREEN} !important;
        font-weight: 800;
        margin-bottom: 5px;
        border-bottom: 2px solid {COLOR_PRIMARY_GREEN};
        padding-bottom: 5px;
    }}
    
    </style>
    """, unsafe_allow_html=True)


def home_page(lang):
    """Displays the home page with bilingual information."""
    inject_page_css(st.session_state.page, HOME_PAGE_BACKGROUND_URL, REC_PAGE_BACKGROUND_URL)
    
    st.title(get_string("title", lang))
    st.subheader(get_string("subtitle", lang))
    st.markdown("---")
    
    col_about, col_ifs = st.columns(2)

    # About Us Card
    with col_about:
        st.markdown(f"""
        <div class="card-base" style="border-top: 5px solid {COLOR_PRIMARY_GREEN}; min-height: 300px;">
            <div class="home-card-header">
                <span class="icon-large" style="color: {COLOR_PRIMARY_GREEN};">🌿</span>
                <h2 style="color: {COLOR_PRIMARY_GREEN} !important; text-shadow: none;">{get_string('about_us_heading', lang)}</h2>
            </div>
            <p style="color: {COLOR_TEXT_MAIN} !important; text-shadow: none;">{get_string('about_us_text', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    # IFS Card
    with col_ifs:
        st.markdown(f"""
        <div class="card-base" style="border-top: 5px solid {COLOR_SECONDARY_GOLD}; min-height: 300px;">
            <div class="home-card-header">
                <span class="icon-large" style="color: {COLOR_SECONDARY_GOLD};">🌾</span>
                <h2 style: "color: {COLOR_SECONDARY_GOLD} !important; text-shadow: none;">{get_string('ifs_heading', lang)}</h2>
            </div>
            <p style="color: {COLOR_TEXT_MAIN} !important; text-shadow: none;">{get_string('ifs_text', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    # --- KVK Collaboration Summary Card ---
    st.markdown(f"""
    <div class="card-base" style="border-top: 5px solid {COLOR_ACCENT_BLUE}; margin-bottom: 30px;">
        <div class="home-card-header">
            <span class="icon-large" style="color: {COLOR_ACCENT_BLUE};">🤝</span>
            <h2 style="color: {COLOR_ACCENT_BLUE} !important; text-shadow: none;">{get_string('home_kvk_heading', lang)}</h2>
        </div>
        <p style="color: {COLOR_TEXT_MAIN} !important; text-shadow: none;">{get_string('home_kvk_text', lang)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Button to navigate to the recommendation page
    if st.button(get_string('get_rec_button', lang), key="rec_button"):
        st.session_state.page = 'recommendation'
        st.rerun()

    # --- NEW: ECONOMIC IMPACT SECTION ---
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: {COLOR_SECONDARY_GOLD} !important; font-weight: 800; text-shadow: none;">{get_string('eco_heading', lang)}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col_eco1, col_eco2, col_eco3 = st.columns(3)
    
    with col_eco1:
        st.markdown(f"""
        <div class="eco-feature-card">
            <h3 style="color: {COLOR_PRIMARY_GREEN} !important;">💵 {get_string('eco_point1_title', lang)}</h3>
            <p style="color: {COLOR_TEXT_MAIN} !important;">{get_string('eco_point1_text', lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_eco2:
        st.markdown(f"""
        <div class="eco-feature-card">
            <h3 style="color: {COLOR_PRIMARY_GREEN} !important;">🔄 {get_string('eco_point2_title', lang)}</h3>
            <p style="color: {COLOR_TEXT_MAIN} !important;">{get_string('eco_point2_text', lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_eco3:
        st.markdown(f"""
        <div class="eco-feature-card">
            <h3 style="color: {COLOR_PRIMARY_GREEN} !important;">🌳 {get_string('eco_point3_title', lang)}</h3>
            <p style="color: {COLOR_TEXT_MAIN} !important;">{get_string('eco_point3_text', lang)}</p>
        </div>
        """, unsafe_allow_html=True)
    # --- END NEW SECTION ---


def recommendation_page(lang):
    """Handles user input and displays recommendations."""
    inject_page_css(st.session_state.page, HOME_PAGE_BACKGROUND_URL, REC_PAGE_BACKGROUND_URL)

    st.title(get_string('input_title', lang))
    # This <p> tag will be white due to the global CSS rule
    st.markdown(f'<p style="font-size: 1.1em;">{get_string("input_prompt", lang)}</p>', unsafe_allow_html=True)
    
    soil_options_en = ['Loamy Soil', 'Sandy Soil', 'Clay Soil', 'Alluvial Soil']
    soil_options_hi = ['दोमट मिट्टी', 'बलुई मिट्टी', 'चिकनी मिट्टी', 'जलोढ़ मिट्टी']
    soil_options_display = soil_options_hi if lang == 'hi' else soil_options_en
    
    season_options_en = ['Kharif', 'Rabi']
    season_options_hi = ['खरीफ', 'रबी']
    season_options_display = season_options_hi if lang == 'hi' else season_options_en

    # --- Input Form (Glass Card) ---
    st.markdown(f'<div class="card-base" style="padding: 20px; border-top: 5px solid {COLOR_SECONDARY_GOLD};">', unsafe_allow_html=True)
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            district = st.selectbox(get_string('select_district', lang), DISTRICTS)
        with col2:
            soil_type_input = st.selectbox(get_string('select_soil', lang), soil_options_display)
        
        crop_season = st.selectbox(get_string('select_season', lang), season_options_display)
        
        submitted = st.form_submit_button(get_string('generate_button', lang))
    st.markdown('</div>', unsafe_allow_html=True)
    
    if submitted:
        crops, trees, flowers = get_recommendations(district, soil_type_input, crop_season)
        lat, lon = get_lat_lon(district)
        weather_data = get_weather_data(lat, lon)
        
        if weather_data:
            st.markdown(f"## {get_string('weather_heading', lang)} {district}")
            current = weather_data['current_weather']
            
            # Current Weather Card (Glass)
            st.markdown(f"""
            <div class="card-base" style="border-top: 5px solid {COLOR_SECONDARY_GOLD}; padding: 20px 30px; margin-top: 10px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 20px;">
                    <div style="flex: 1; min-width: 150px; text-align: center; border-right: 1px solid rgba(255,255,255,0.2);">
                        <p style="margin: 0; font-size: 0.9em;"> {get_string('temp', lang)}</p>
                        <h3 style="margin-top: 5px; color: {COLOR_TEXT_MAIN}; font-size: 2.0em;">{current['temperature']}°C</h3>
                    </div>
                    <div style="flex: 1; min-width: 150px; text-align: center; border-right: 1px solid rgba(255,255,255,0.2);">
                        <p style="margin: 0; font-size: 0.9em;"> {get_string('wind', lang)}</p>
                        <h3 style="margin-top: 5px; color: {COLOR_TEXT_MAIN}; font-size: 2.0em;">{current['windspeed']} km/h</h3>
                    </div>
                    <div style="flex: 1; min-width: 150px; text-align: center;">
                        <p style="margin: 0; font-size: 0.9em;"> {get_string('time', lang)}</p>
                        <h3 style="margin-top: 5px; color: {COLOR_TEXT_MAIN}; font-size: 2.0em;">{datetime.fromisoformat(current['time']).strftime('%I:%M %p')}</h3>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**{get_string('daily_forecast', lang)}**") 
            daily = weather_data['daily']
            df_forecast = pd.DataFrame({
                get_string('date_col', lang): [datetime.fromisoformat(d).strftime('%a, %b %d') for d in daily['time']],
                get_string('max_temp_col', lang): daily['temperature_2m_max'],
                get_string('min_temp_col', lang): daily['temperature_2m_min'],
                get_string('rain_col', lang): daily['precipitation_sum'],
            }).set_index(get_string('date_col', lang))
            
            st.dataframe(df_forecast, height=300, use_container_width=True)

        st.markdown("---")
        
        st.header(get_string('rec_heading', lang))
        
        tab_crops, tab_trees, tab_flowers, tab_ifs = st.tabs([
            get_string('tab_crops', lang), 
            get_string('tab_trees', lang), 
            get_string('tab_flowers', lang), 
            get_string('tab_ifs', lang)
        ])
        
        with tab_crops:
            st.subheader(get_string('crop_rec_subheader', lang).format(crop_season, soil_type_input))
            if crops:
                for i, crop in enumerate(crops):
                    req_df = df_field_crop[df_field_crop['Crop'] == crop]
                    req = req_df['Soil_Water_pH'].iloc[0] if not req_df.empty else "General requirements."
                    display_recommendation_card(f"{i+1}. {crop}", req, COLOR_PRIMARY_GREEN)
            else:
                st.warning(get_string('no_match', lang))

        with tab_trees:
            st.subheader(get_string('tree_rec_subheader', lang).format(soil_type_input))
            if trees:
                for i, tree in enumerate(trees):
                    roi = ROI_MAP.get(tree, "N/A")
                    req_df = df_commercial_trees[df_commercial_trees['Tree'] == tree]
                    req = req_df['Soil_Water_pH'].iloc[0] if not req_df.empty else "General requirements."
                    display_recommendation_card(f"{i+1}. {tree.split('(')[0].strip()}", req, COLOR_ACCENT_BLUE, roi=roi)
            else:
                st.warning(get_string('no_tree_match', lang))
                
        with tab_flowers:
            st.subheader(get_string('flower_rec_subheader', lang).format(soil_type_input))
            if flowers:
                for i, flower in enumerate(flowers):
                    req_df = df_flori[df_flori['Flower'].str.contains(flower, case=False, na=False)]
                    req = req_df['Soil_Water_pH'].iloc[0] if not req_df.empty else "General requirements."
                    display_recommendation_card(f"{i+1}. {flower}", req, COLOR_ACCENT_PINK) 
            else:
                st.warning(get_string('no_flower_match', lang))

        with tab_ifs:
            st.header(get_string('interaction_title', lang))
            st.write(get_string('interaction_desc', lang))
            
            all_recommendations = set(crops + trees + flowers)
            found_interactions = []
            
            for item in all_recommendations:
                if item in COMPLEMENTARY_INTERACTIONS:
                    for complement in COMPLEMENTARY_INTERACTIONS[item]:
                        if complement in all_recommendations or complement in ['Marigold', 'Turmeric']:
                            found_interactions.append((item, complement, f"{item} benefits {complement} (e.g., pest control/soil health)."))
            
            if found_interactions:
                for item1, item2, reason in found_interactions:
                    st.markdown(f"""
                    <div class="rec-item-card" style="border-left: 8px solid {COLOR_ACCENT_BLUE}; background-color: rgba(230, 247, 255, 0.2); margin-bottom: 15px; padding: 15px;">
                        <h5 style="color: {COLOR_ACCENT_BLUE}; margin: 0; font-weight: bold; font-size: 1.1em;">{item1} + {item2}</h5>
                        <p style="margin: 5px 0 0 0; font-size: 0.95em;">{reason}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No direct complementary interactions found among your top recommended items.")
                
    
    st.markdown("---")
    if st.button(get_string('back_button', lang), key="rec_back_button"):
        st.session_state.page = 'home'
        st.rerun()

def about_page(lang):
    """Displays the About Us content."""
    inject_page_css(st.session_state.page, HOME_PAGE_BACKGROUND_URL, REC_PAGE_BACKGROUND_URL)
    
    st.title(get_string('nav_about', lang))
    
    st.markdown(f"""
    <div class="card-base" style="border-top: 5px solid {COLOR_SECONDARY_GOLD};">
        <h2 style="color: {COLOR_SECONDARY_GOLD} !important; text-shadow: none;">{get_string('about_page_heading', lang)}</h2>
        <p style="font-size: 1.1em; color: {COLOR_TEXT_MAIN} !important; text-shadow: none;">{get_string('about_page_text1', lang)}</p>
        <p style="font-size: 1.1em; color: {COLOR_TEXT_MAIN} !important; text-shadow: none;">{get_string('about_page_text2', lang)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    
def collaboration_page(lang):
    """Displays KVK Collaboration details."""
    inject_page_css(st.session_state.page, HOME_PAGE_BACKGROUND_URL, REC_PAGE_BACKGROUND_URL)

    st.title(get_string('nav_collaboration', lang))
    
    st.markdown(f"""
    <div class="card-base" style="border-top: 5px solid {COLOR_ACCENT_BLUE};">
        <h2 style="color: {COLOR_ACCENT_BLUE} !important; text-shadow: none;">{get_string('collaboration_page_heading', lang)}</h2>
        <p style="font-size: 1.1em; color: {COLOR_TEXT_MAIN} !important; text-shadow: none;">{get_string('collaboration_page_text_main', lang)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="card-base" style="margin-top: -20px;">
        <h3 style="margin-top: 0; color: {COLOR_PRIMARY_GREEN} !important; text-shadow: none;">{get_string('collaboration_kvk_important', lang)}</h3>
        <ul style="padding-left: 20px; color: {COLOR_TEXT_MAIN} !important; text-shadow: none;">
            <li style="color: {COLOR_TEXT_MAIN} !important; text-shadow: none;">{get_string('collaboration_page_list1', lang)}</li>
            <li style="color: {COLOR_TEXT_MAIN} !important; text-shadow: none;">{get_string('collaboration_page_list2', lang)}</li>
            <li style="color: {COLOR_TEXT_MAIN} !important; text-shadow: none;">{get_string('collaboration_page_list3', lang)}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# --- 8. Main Application Flow ---

def main():
    """Main application loop to handle page navigation and state."""
    
    # Set page config
    st.set_page_config(
        page_title="Agro-Assist",
        page_icon="🌿",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state variables
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'lang' not in st.session_state:
        st.session_state.lang = 'en' # Default to English
        
    current_lang = st.session_state.lang

    # --- Sidebar Navigation & Language Switcher ---
    with st.sidebar:
        st.markdown(f'<h1 class="sidebar-heading">{get_string("title", current_lang)}</h1>', unsafe_allow_html=True)
        
        st.markdown("### Select Language | भाषा चुनें")
        selected_lang_label = st.radio(
            "Language", 
            ('English', 'हिन्दी'), 
            index=0 if st.session_state.lang == 'en' else 1, 
            key="lang_radio", 
            label_visibility="collapsed"
        )
        new_lang = 'en' if selected_lang_label == 'English' else 'hi'
        
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun() 
        
        current_lang = st.session_state.lang # Ensure current_lang is the latest

        st.markdown("---")
        
        st.markdown("### Navigation")
        
        # Updated Navigation Options (Contact Us Removed)
        nav_options = {
            get_string('nav_home', current_lang): 'home',
            get_string('nav_about', current_lang): 'about',
            get_string('nav_collaboration', current_lang): 'collaboration',
            "Get Recommendations": 'recommendation' 
        }
        
        # Handle cases where the page state might be 'contact' from a previous version
        if st.session_state.page == 'contact':
            st.session_state.page = 'home'
            
        try:
            current_index = list(nav_options.values()).index(st.session_state.page)
        except ValueError:
            current_index = 0 # Default to home
        
        page_selection = st.radio(
            "Go to", 
            list(nav_options.keys()), 
            index=current_index, 
            key="page_selector", 
            label_visibility="collapsed"
        )
        
        if page_selection and nav_options[page_selection] != st.session_state.page:
            st.session_state.page = nav_options[page_selection]
            st.rerun()


    # --- Page rendering based on state ---
    if st.session_state.page == 'home':
        home_page(current_lang)
    elif st.session_state.page == 'recommendation':
        recommendation_page(current_lang)
    elif st.session_state.page == 'about':
        about_page(current_lang)
    elif st.session_state.page == 'collaboration':
        collaboration_page(current_lang)
    

if __name__ == "__main__":
    main()