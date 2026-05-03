from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import random
from datetime import datetime, timedelta
import re

app = Flask(__name__)
CORS(app)

# ============================================================
# MODULE SCRAPER - Données simulées mais structure réelle
# (Remplace par vrai scraping quand tu veux)
# ============================================================

LEAGUES = {
    "premier-league": {"name": "Premier League", "country": "England"},
    "la-liga": {"name": "La Liga", "country": "Spain"},
    "serie-a": {"name": "Serie A", "country": "Italy"},
    "bundesliga": {"name": "Bundesliga", "country": "Germany"},
    "ligue-1": {"name": "Ligue 1", "country": "France"},
    "champions-league": {"name": "Champions League", "country": "Europe"}
}

TEAMS_DB = {
    "premier-league": [
        "Manchester City", "Liverpool", "Arsenal", "Chelsea", "Manchester United",
        "Tottenham", "Newcastle", "Aston Villa", "Brighton", "West Ham",
        "Brentford", "Crystal Palace", "Fulham", "Everton", "Nottingham Forest",
        "Bournemouth", "Wolves", "Leicester", "Ipswich", "Southampton"
    ],
    "la-liga": [
        "Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla", "Real Sociedad",
        "Villarreal", "Real Betis", "Athletic Bilbao", "Valencia", "Celta Vigo",
        "Getafe", "Osasuna", "Rayo Vallecano", "Mallorca", "Las Palmas",
        "Alaves", "Girona", "Leganes", "Espanyol", "Valladolid"
    ],
    "serie-a": [
        "Inter Milan", "AC Milan", "Juventus", "Napoli", "Roma",
        "Lazio", "Atalanta", "Fiorentina", "Bologna", "Torino",
        "Monza", "Genoa", "Sassuolo", "Udinese", "Empoli",
        "Lecce", "Verona", "Cagliari", "Frosinone", "Salernitana"
    ],
    "bundesliga": [
        "Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen", "Eintracht Frankfurt",
        "Wolfsburg", "Freiburg", "Union Berlin", "Monchengladbach", "Mainz",
        "Hoffenheim", "Augsburg", "Stuttgart", "Bochum", "Heidenheim",
        "Werder Bremen", "Darmstadt", "Koln", "Holstein Kiel", "Bielefeld"
    ],
    "ligue-1": [
        "Paris Saint-Germain", "Monaco", "Marseille", "Rennes", "Lille",
        "Nice", "Lyon", "Lens", "Strasbourg", "Nantes",
        "Montpellier", "Reims", "Brest", "Toulouse", "Le Havre",
        "Metz", "Lorient", "Clermont", "Auxerre", "Angers"
    ],
    "champions-league": [
        "Real Madrid", "Bayern Munich", "Manchester City", "Paris Saint-Germain", "Barcelona",
        "Liverpool", "Arsenal", "Inter Milan", "Borussia Dortmund", "Atletico Madrid",
        "RB Leipzig", "Porto", "Benfica", "Juventus", "AC Milan",
        "Napoli", "Chelsea", "Manchester United", "Tottenham", "Ajax"
    ]
}

def generate_match_data(home_team, away_team, league_id):
    """Génère des données réalistes pour un match"""
    # Forme des équipes (0-100)
    home_form = random.randint(45, 95)
    away_form = random.randint(45, 95)

    # Stats moyennes
    home_avg_goals_scored = round(random.uniform(1.2, 2.8), 2)
    home_avg_goals_conceded = round(random.uniform(0.8, 1.8), 2)
    away_avg_goals_scored = round(random.uniform(1.0, 2.5), 2)
    away_avg_goals_conceded = round(random.uniform(0.9, 1.9), 2)

    # Head-to-head simulé
    h2h = []
    for i in range(5):
        h2h.append({
            "date": (datetime.now() - timedelta(days=180+i*30)).strftime("%d/%m/%Y"),
            "home": home_team if i % 2 == 0 else away_team,
            "away": away_team if i % 2 == 0 else home_team,
            "score": f"{random.randint(0, 3)}-{random.randint(0, 3)}"
        })

    # Derniers matchs
    def last_matches(team, is_home):
        matches = []
        for i in range(5):
            opponent = random.choice([t for t in TEAMS_DB[league_id] if t != team])
            gf = random.randint(0, 4)
            ga = random.randint(0, 3)
            result = "W" if gf > ga else ("D" if gf == ga else "L")
            matches.append({
                "date": (datetime.now() - timedelta(days=7+i*7)).strftime("%d/%m/%Y"),
                "opponent": opponent,
                "venue": "H" if is_home else "A",
                "score": f"{gf}-{ga}",
                "result": result
            })
        return matches

    return {
        "home_team": home_team,
        "away_team": away_team,
        "league": LEAGUES[league_id]["name"],
        "match_date": (datetime.now() + timedelta(days=random.randint(1, 7))).strftime("%d/%m/%Y %H:%M"),
        "home_form": home_form,
        "away_form": away_form,
        "home_avg_goals_scored": home_avg_goals_scored,
        "home_avg_goals_conceded": home_avg_goals_conceded,
        "away_avg_goals_scored": away_avg_goals_scored,
        "away_avg_goals_conceded": away_avg_goals_conceded,
        "home_possession": random.randint(48, 62),
        "away_possession": random.randint(38, 52),
        "home_shots_per_game": round(random.uniform(10, 18), 1),
        "away_shots_per_game": round(random.uniform(8, 15), 1),
        "h2h": h2h,
        "home_last_5": last_matches(home_team, True),
        "away_last_5": last_matches(away_team, False)
    }

def ml_predict(match_data):
    """Algorithme ML simple pour prédiction"""
    home_strength = (
        match_data["home_form"] * 0.3 +
        match_data["home_avg_goals_scored"] * 15 +
        (2 - match_data["home_avg_goals_conceded"]) * 10 +
        match_data["home_possession"] * 0.3
    )

    away_strength = (
        match_data["away_form"] * 0.3 +
        match_data["away_avg_goals_scored"] * 15 +
        (2 - match_data["away_avg_goals_conceded"]) * 10 +
        match_data["away_possession"] * 0.3
    )

    # Prédiction 1X2
    total = home_strength + away_strength
    home_prob = min(max(home_strength / total * 100, 15), 70)
    away_prob = min(max(away_strength / total * 100, 15), 70)
    draw_prob = 100 - home_prob - away_prob

    if draw_prob < 10:
        draw_prob = 10
        home_prob = home_prob - 5
        away_prob = away_prob - 5

    # Over/Under 2.5
    expected_goals = match_data["home_avg_goals_scored"] + match_data["away_avg_goals_scored"]
    over_prob = min(max(expected_goals / 3 * 100, 25), 75)
    under_prob = 100 - over_prob

    # BTTS
    btts_prob = min(max(
        (match_data["home_avg_goals_scored"] + match_data["away_avg_goals_scored"]) / 4 * 100,
        30
    ), 70)

    # Best pick
    predictions = {
        "1": home_prob,
        "X": draw_prob,
        "2": away_prob,
        "Over 2.5": over_prob,
        "Under 2.5": under_prob,
        "BTTS Yes": btts_prob,
        "BTTS No": 100 - btts_prob
    }
    best_pick = max(predictions, key=predictions.get)

    # Risk level
    confidence = predictions[best_pick]
    if confidence >= 70:
        risk = "SAFE"
        risk_color = "#22c55e"
    elif confidence >= 55:
        risk = "MODERATE"
        risk_color = "#f59e0b"
    else:
        risk = "RISKY"
        risk_color = "#ef4444"

    return {
        "1x2": {
            "1": round(home_prob, 1),
            "X": round(draw_prob, 1),
            "2": round(away_prob, 1)
        },
        "over_under": {
            "over_2_5": round(over_prob, 1),
            "under_2_5": round(under_prob, 1)
        },
        "btts": {
            "yes": round(btts_prob, 1),
            "no": round(100 - btts_prob, 1)
        },
        "best_pick": best_pick,
        "confidence": round(confidence, 1),
        "risk_level": risk,
        "risk_color": risk_color,
        "expected_goals": round(expected_goals, 2)
    }

# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/leagues")
def get_leagues():
    return jsonify(LEAGUES)

@app.route("/api/teams/<league_id>")
def get_teams(league_id):
    if league_id in TEAMS_DB:
        return jsonify(TEAMS_DB[league_id])
    return jsonify({"error": "League not found"}), 404

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.json
    home_team = data.get("home_team")
    away_team = data.get("away_team")
    league_id = data.get("league_id", "premier-league")

    if not home_team or not away_team:
        return jsonify({"error": "Teams required"}), 400

    match_data = generate_match_data(home_team, away_team, league_id)
    prediction = ml_predict(match_data)

    return jsonify({
        "match": match_data,
        "prediction": prediction
    })

@app.route("/api/today-matches")
def today_matches():
    """Retourne les matchs du jour simulés"""
    matches = []
    leagues = list(LEAGUES.keys())[:4]

    for league_id in leagues:
        teams = TEAMS_DB[league_id]
        for i in range(3):
            home = random.choice(teams)
            away = random.choice([t for t in teams if t != home])
            match_data = generate_match_data(home, away, league_id)
            prediction = ml_predict(match_data)
            matches.append({
                "match": match_data,
                "prediction": prediction
            })

    return jsonify(matches)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)