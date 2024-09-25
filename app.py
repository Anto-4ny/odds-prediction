from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)

# Function to get odds data (using BeautifulSoup or Selenium)
def get_odds_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    odds_table = soup.find('table', {'class': 'odds_table_class'})  # Replace with actual table class
    odds_data = []

    for row in odds_table.find_all('tr'):
        columns = row.find_all('td')
        odds = [col.text for col in columns]
        odds_data.append(odds)
    
    return odds_data

# Analyzing odds and making predictions
def analyze_odds(odds_data):
    df = pd.DataFrame(odds_data, columns=['Match', 'Team1_Odds', 'Draw_Odds', 'Team2_Odds'])
    
    # Convert odds to numeric
    df['Team1_Odds'] = pd.to_numeric(df['Team1_Odds'], errors='coerce')
    df['Draw_Odds'] = pd.to_numeric(df['Draw_Odds'], errors='coerce')
    df['Team2_Odds'] = pd.to_numeric(df['Team2_Odds'], errors='coerce')

    # Simple strategy: Pick the team with the lowest odds
    df['Prediction'] = df[['Team1_Odds', 'Draw_Odds', 'Team2_Odds']].idxmin(axis=1)

    return df[['Match', 'Prediction']].to_dict('records')

# Route to serve the front-end HTML
@app.route('/')
def index():
    return render_template('index.html')

# API route to handle predictions
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        odds_data = get_odds_data(url)
        predictions = analyze_odds(odds_data)
        return jsonify({"predictions": predictions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
  
