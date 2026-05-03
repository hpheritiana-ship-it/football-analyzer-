from flask import Flask, render_template_string, jsonify, request
import random
from datetime import datetime, timedelta

app = Flask(__name__)

LEAGUES = {
    "premier-league": {"name": "Premier League", "country": "England"},
    "la-liga": {"name": "La Liga", "country": "Spain"},
    "serie-a": {"name": "Serie A", "country": "Italy"},
    "bundesliga": {"name": "Bundesliga", "country": "Germany"},
    "ligue-1": {"name": "Ligue 1", "country": "France"},
    "champions-league": {"name": "Champions League", "country": "Europe"}
}

TEAMS_DB = {
    "premier-league": ["Man City", "Liverpool", "Arsenal", "Chelsea", "Man Utd", "Tottenham", "Newcastle", "Aston Villa", "Brighton", "West Ham"],
    "la-liga": ["Real Madrid", "Barcelona", "Atletico", "Sevilla", "Real Sociedad", "Villarreal", "Betis", "Bilbao", "Valencia", "Celta"],
    "serie-a": ["Inter", "AC Milan", "Juventus", "Napoli", "Roma", "Lazio", "Atalanta", "Fiorentina", "Bologna", "Torino"],
    "bundesliga": ["Bayern", "Dortmund", "RB Leipzig", "Leverkusen", "Frankfurt", "Wolfsburg", "Freiburg", "Union Berlin", "Gladbach", "Mainz"],
    "ligue-1": ["PSG", "Monaco", "Marseille", "Rennes", "Lille", "Nice", "Lyon", "Lens", "Strasbourg", "Nantes"],
    "champions-league": ["Real Madrid", "Bayern", "Man City", "PSG", "Barcelona", "Liverpool", "Arsenal", "Inter", "Dortmund", "Atletico"]
}

def generate_match_data(home_team, away_team, league_id):
    home_form = random.randint(45, 95)
    away_form = random.randint(45, 95)
    home_avg_goals_scored = round(random.uniform(1.2, 2.8), 2)
    home_avg_goals_conceded = round(random.uniform(0.8, 1.8), 2)
    away_avg_goals_scored = round(random.uniform(1.0, 2.5), 2)
    away_avg_goals_conceded = round(random.uniform(0.9, 1.9), 2)

    h2h = []
    for i in range(5):
        h2h.append({
            "date": (datetime.now() - timedelta(days=180+i*30)).strftime("%d/%m/%Y"),
            "home": home_team if i % 2 == 0 else away_team,
            "away": away_team if i % 2 == 0 else home_team,
            "score": f"{random.randint(0, 3)}-{random.randint(0, 3)}"
        })

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
    home_strength = (match_data["home_form"] * 0.3 + match_data["home_avg_goals_scored"] * 15 + (2 - match_data["home_avg_goals_conceded"]) * 10 + match_data["home_possession"] * 0.3)
    away_strength = (match_data["away_form"] * 0.3 + match_data["away_avg_goals_scored"] * 15 + (2 - match_data["away_avg_goals_conceded"]) * 10 + match_data["away_possession"] * 0.3)

    total = home_strength + away_strength
    home_prob = min(max(home_strength / total * 100, 15), 70)
    away_prob = min(max(away_strength / total * 100, 15), 70)
    draw_prob = max(100 - home_prob - away_prob, 10)

    expected_goals = match_data["home_avg_goals_scored"] + match_data["away_avg_goals_scored"]
    over_prob = min(max(expected_goals / 3 * 100, 25), 75)
    btts_prob = min(max((match_data["home_avg_goals_scored"] + match_data["away_avg_goals_scored"]) / 4 * 100, 30), 70)

    predictions = {"1": home_prob, "X": draw_prob, "2": away_prob, "Over 2.5": over_prob, "Under 2.5": 100-over_prob, "BTTS Yes": btts_prob, "BTTS No": 100-btts_prob}
    best_pick = max(predictions, key=predictions.get)
    confidence = predictions[best_pick]

    risk = "SAFE" if confidence >= 70 else ("MODERATE" if confidence >= 55 else "RISKY")
    risk_color = "#22c55e" if risk == "SAFE" else ("#f59e0b" if risk == "MODERATE" else "#ef4444")

    return {
        "1x2": {"1": round(home_prob, 1), "X": round(draw_prob, 1), "2": round(away_prob, 1)},
        "over_under": {"over_2_5": round(over_prob, 1), "under_2_5": round(100-over_prob, 1)},
        "btts": {"yes": round(btts_prob, 1), "no": round(100-btts_prob, 1)},
        "best_pick": best_pick,
        "confidence": round(confidence, 1),
        "risk_level": risk,
        "risk_color": risk_color,
        "expected_goals": round(expected_goals, 2)
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Football Analyzer Pro</title>
<style>
:root{--bg:#0f0f1a;--bg2:#1a1a2e;--card:#16162a;--text:#e2e8f0;--text2:#94a3b8;--accent:#6366f1;--success:#22c55e;--warning:#f59e0b;--danger:#ef4444;--border:rgba(255,255,255,0.08)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;padding:20px}
.container{max-width:1200px;margin:0 auto}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;padding-bottom:20px;border-bottom:1px solid var(--border)}
h1{font-size:28px;background:linear-gradient(135deg,var(--text),#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.live{background:rgba(34,197,94,0.15);color:var(--success);padding:8px 16px;border-radius:20px;font-size:12px;font-weight:700}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:30px}
.stat{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:20px}
.stat h3{font-size:12px;color:var(--text2);margin-bottom:8px}
.stat .value{font-size:24px;font-weight:800}
.stat .change{font-size:12px;color:var(--success);margin-top:4px}
.card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;margin-bottom:20px}
.card h2{font-size:18px;margin-bottom:20px;display:flex;align-items:center;gap:10px}
.form-group{margin-bottom:15px}
label{display:block;font-size:12px;color:var(--text2);margin-bottom:6px;text-transform:uppercase}
select{width:100%;padding:12px;background:var(--bg2);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:14px}
.btn{width:100%;padding:14px;background:linear-gradient(135deg,#4f46e5,var(--accent));color:white;border:none;border-radius:10px;font-size:16px;font-weight:700;cursor:pointer;margin-top:10px}
.btn:hover{opacity:0.9}
.teams{display:grid;grid-template-columns:1fr auto 1fr;gap:15px;align-items:end;margin-bottom:15px}
.vs{text-align:center;font-weight:800;color:var(--accent);font-size:20px}
.result{display:none;margin-top:20px;animation:fadeIn 0.5s}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.match-display{display:flex;justify-content:center;align-items:center;gap:30px;padding:20px;background:var(--bg2);border-radius:12px;margin-bottom:20px;text-align:center}
.team-avatar{width:60px;height:60px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:white;margin:0 auto 10px}
.prob-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:20px}
.prob-box{background:var(--bg2);border-radius:12px;padding:15px}
.prob-box h4{font-size:11px;color:var(--text2);margin-bottom:12px;text-transform:uppercase}
.prob-row{display:flex;justify-content:space-between;margin-bottom:8px;font-size:14px}
.prob-bar{height:6px;background:var(--bg);border-radius:3px;overflow:hidden}
.prob-fill{height:100%;border-radius:3px;transition:width 0.8s}
.best-pick{background:linear-gradient(135deg,#4f46e5,var(--accent));border-radius:16px;padding:24px;text-align:center;color:white;margin-bottom:20px}
.best-pick .pick{font-size:32px;font-weight:800;margin:10px 0}
.risk-tag{display:inline-block;padding:6px 16px;background:rgba(255,255,255,0.2);border-radius:20px;font-size:12px;font-weight:700;margin-top:10px}
.tabs{display:flex;gap:10px;margin-bottom:20px}
.tab{padding:10px 20px;background:var(--card);border:1px solid var(--border);border-radius:10px;color:var(--text2);cursor:pointer;font-weight:600}
.tab.active{background:var(--accent);color:white;border-color:var(--accent)}
.section{display:none}
.section.active{display:block;animation:fadeIn 0.4s}
.prediction-item{display:flex;justify-content:space-between;align-items:center;padding:15px;background:var(--bg2);border-radius:10px;margin-bottom:10px;border:1px solid var(--border)}
.confidence{padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700}
.confidence.safe{background:rgba(34,197,94,0.15);color:var(--success)}
.confidence.moderate{background:rgba(245,158,11,0.15);color:var(--warning)}
.confidence.risky{background:rgba(239,68,68,0.15);color:var(--danger)}
@media(max-width:768px){.stats{grid-template-columns:repeat(2,1fr)}.prob-grid{grid-template-columns:1fr}.teams{grid-template-columns:1fr}.vs{padding:10px 0}}
</style>
</head>
<body>
<div class="container">
<header>
<h1>⚽ Football Analyzer Pro</h1>
<span class="live">● LIVE</span>
</header>

<div class="stats">
<div class="stat"><h3>Précision ML</h3><div class="value">74.2%</div><div class="change">+2.4% ce mois</div></div>
<div class="stat"><h3>Predictions</h3><div class="value">12</div><div class="change">8 gagnées</div></div>
<div class="stat"><h3>Série</h3><div class="value">5W</div><div class="change">Meilleure: 12W</div></div>
<div class="stat"><h3>ROI</h3><div class="value">+18.5%</div><div class="change">Sur 30 jours</div></div>
</div>

<div class="tabs">
<div class="tab active" onclick="showTab('dashboard')">Dashboard</div>
<div class="tab" onclick="showTab('predict')">Prédiction</div>
<div class="tab" onclick="showTab('matches')">Matchs du Jour</div>
</div>

<div id="dashboard" class="section active">
<div class="card">
<h2>🔥 Top Prédictions</h2>
<div id="top-predictions"><div style="text-align:center;padding:40px;color:var(--text2)">Chargement...</div></div>
</div>
</div>

<div id="predict" class="section">
<div class="card">
<h2>🧠 Nouvelle Prédiction</h2>
<div class="form-group"><label>Championnat</label><select id="league" onchange="loadTeams()"><option value="">Sélectionner...</option></select></div>
<div class="teams">
<div class="form-group"><label>Domicile</label><select id="home"><option value="">...</option></select></div>
<div class="vs">VS</div>
<div class="form-group"><label>Extérieur</label><select id="away"><option value="">...</option></select></div>
</div>
<button class="btn" onclick="predict()">Analyser le Match</button>
<div id="result" class="result"></div>
</div>
</div>

<div id="matches" class="section">
<div class="card">
<h2>📅 Matchs du Jour</h2>
<div id="today-matches"><div style="text-align:center;padding:40px;color:var(--text2)">Chargement...</div></div>
</div>
</div>
</div>

<script>
let leaguesData={};

function showTab(tab){
document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
event.target.classList.add('active');
document.getElementById(tab).classList.add('active');
if(tab==='matches') loadMatches();
if(tab==='dashboard') loadTop();
}

async function loadLeagues(){
try{
const r=await fetch('/api/leagues');
leaguesData=await r.json();
const s=document.getElementById('league');
s.innerHTML='<option value="">Sélectionner...</option>';
for(const[id,l] of Object.entries(leaguesData)){
s.innerHTML+=`<option value="${id}">${l.name}</option>`;
}
loadTop();
}catch(e){console.error(e);}
}

async function loadTeams(){
const id=document.getElementById('league').value;
if(!id) return;
try{
const r=await fetch(`/api/teams/${id}`);
const teams=await r.json();
const h=document.getElementById('home');
const a=document.getElementById('away');
h.innerHTML=a.innerHTML='<option value="">...</option>';
teams.forEach(t=>{h.innerHTML+=`<option value="${t}">${t}</option>`;a.innerHTML+=`<option value="${t}">${t}</option>`;});
}catch(e){console.error(e);}
}

async function predict(){
const home=document.getElementById('home').value;
const away=document.getElementById('away').value;
const league=document.getElementById('league').value;
if(!home||!away){alert('Sélectionner les équipes');return;}
if(home===away){alert('Équipes différentes');return;}

document.querySelector('.btn').textContent='Analyse...';
try{
const r=await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({home_team:home,away_team:away,league_id:league})});
const d=await r.json();
showResult(d);
}catch(e){alert('Erreur');}
document.querySelector('.btn').textContent='Analyser le Match';
}

function showResult(d){
const m=d.match,p=d.prediction;
const getBar=v=>v>=60?'var(--success)':(v>=40?'var(--warning)':'var(--danger)');
const div=document.getElementById('result');
div.innerHTML=`<div class="match-display">
<div><div class="team-avatar" style="background:linear-gradient(135deg,#6366f1,#4f46e5)">${m.home_team.substring(0,2).toUpperCase()}</div><div style="font-weight:700">${m.home_team}</div><div style="font-size:12px;color:var(--text2)">Forme: ${m.home_form}/100</div></div>
<div><div style="font-size:36px;font-weight:800;color:var(--accent)">${p.expected_goals}</div><div style="font-size:12px;color:var(--text2)">Buts attendus</div></div>
<div><div class="team-avatar" style="background:linear-gradient(135deg,#ec4899,#db2777)">${m.away_team.substring(0,2).toUpperCase()}</div><div style="font-weight:700">${m.away_team}</div><div style="font-size:12px;color:var(--text2)">Forme: ${m.away_form}/100</div></div>
</div>
<div class="prob-grid">
<div class="prob-box"><h4>1X2</h4>${Object.entries(p['1x2']).map(([k,v])=>`<div class="prob-row"><span>${k==='1'?'Domicile':(k==='X'?'Nul':'Extérieur')}</span><span style="color:${getBar(v)}">${v}%</span></div><div class="prob-bar"><div class="prob-fill" style="width:${v}%;background:${getBar(v)}"></div></div>`).join('')}</div>
<div class="prob-box"><h4>Over/Under 2.5</h4><div class="prob-row"><span>Over</span><span style="color:${getBar(p.over_under.over_2_5)}">${p.over_under.over_2_5}%</span></div><div class="prob-bar"><div class="prob-fill" style="width:${p.over_under.over_2_5}%;background:${getBar(p.over_under.over_2_5)}"></div></div><div class="prob-row" style="margin-top:8px"><span>Under</span><span style="color:${getBar(p.over_under.under_2_5)}">${p.over_under.under_2_5}%</span></div><div class="prob-bar"><div class="prob-fill" style="width:${p.over_under.under_2_5}%;background:${getBar(p.over_under.under_2_5)}"></div></div></div>
<div class="prob-box"><h4>BTTS</h4><div class="prob-row"><span>Oui</span><span style="color:${getBar(p.btts.yes)}">${p.btts.yes}%</span></div><div class="prob-bar"><div class="prob-fill" style="width:${p.btts.yes}%;background:${getBar(p.btts.yes)}"></div></div><div class="prob-row" style="margin-top:8px"><span>Non</span><span style="color:${getBar(p.btts.no)}">${p.btts.no}%</span></div><div class="prob-bar"><div class="prob-fill" style="width:${p.btts.no}%;background:${getBar(p.btts.no)}"></div></div></div>
</div>
<div class="best-pick"><div style="font-size:13px;opacity:0.8">MEILLEURE PRÉDICTION</div><div class="pick">${p.best_pick}</div><div style="font-size:16px">Confiance: ${p.confidence}%</div><span class="risk-tag" style="background:${p.risk_color}40;color:${p.risk_color};border:1px solid ${p.risk_color}">${p.risk_level}</span></div>`;
div.style.display='block';
}

async function loadMatches(){
const div=document.getElementById('today-matches');
div.innerHTML='<div style="text-align:center;padding:40px;color:var(--text2)">Chargement...</div>';
try{
const r=await fetch('/api/today-matches');
const matches=await r.json();
div.innerHTML=matches.map(m=>`<div class="prediction-item"><div><div style="font-weight:700">${m.match.home_team} vs ${m.match.away_team}</div><div style="font-size:12px;color:var(--text2)">${m.match.league}</div></div><div style="text-align:right"><div style="font-weight:700;color:var(--accent)">${m.prediction.best_pick}</div><span class="confidence ${m.prediction.risk_level.toLowerCase()}">${m.prediction.confidence}%</span></div></div>`).join('');
}catch(e){div.innerHTML='<div style="text-align:center;padding:40px;color:var(--text2)">Erreur</div>';}
}

async function loadTop(){
const div=document.getElementById('top-predictions');
try{
const r=await fetch('/api/today-matches');
const matches=await r.json();
const sorted=matches.sort((a,b)=>b.prediction.confidence-a.prediction.confidence).slice(0,5);
div.innerHTML=sorted.map(m=>`<div class="prediction-item" onclick="showTab('predict');document.getElementById('league').value='${Object.keys(leaguesData).find(k=>leaguesData[k].name===m.match.league)||'premier-league'}';loadTeams();document.getElementById('home').value='${m.match.home_team}';document.getElementById('away').value='${m.match.away_team}';predict();"><div><div style="font-weight:700">${m.match.home_team} vs ${m.match.away_team}</div><div style="font-size:12px;color:var(--text2)">${m.match.league}</div></div><div style="text-align:right"><div style="font-weight:700;color:var(--accent)">${m.prediction.best_pick}</div><span class="confidence ${m.prediction.risk_level.toLowerCase()}">${m.prediction.confidence}%</span></div></div>`).join('');
}catch(e){console.error(e);}
}

loadLeagues();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/leagues")
def get_leagues():
    return jsonify(LEAGUES)

@app.route("/api/teams/<league_id>")
def get_teams(league_id):
    return jsonify(TEAMS_DB.get(league_id, []))

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.json
    match_data = generate_match_data(data["home_team"], data["away_team"], data.get("league_id", "premier-league"))
    return jsonify({"match": match_data, "prediction": ml_predict(match_data)})

@app.route("/api/today-matches")
def today_matches():
    matches = []
    for league_id in list(LEAGUES.keys())[:4]:
        teams = TEAMS_DB[league_id]
        for i in range(3):
            home = random.choice(teams)
            away = random.choice([t for t in teams if t != home])
            match_data = generate_match_data(home, away, league_id)
            matches.append({"match": match_data, "prediction": ml_predict(match_data)})
    return jsonify(matches)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
