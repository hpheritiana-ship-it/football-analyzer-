
// ========== STATE ==========
let currentLeague = '';
let leaguesData = {};

// ========== NAVIGATION ==========
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-links li').forEach(l => l.classList.remove('active'));

    document.getElementById(sectionId).classList.add('active');
    event.currentTarget.classList.add('active');

    const titles = {
        'dashboard': 'Dashboard',
        'predictor': 'Prédiction',
        'matches': 'Matchs du Jour',
        'history': 'Historique'
    };
    document.getElementById('page-title').textContent = titles[sectionId];

    if (sectionId === 'matches') loadTodayMatches();
    if (sectionId === 'dashboard') loadTopPredictions();
}

// ========== INIT ==========
document.addEventListener('DOMContentLoaded', () => {
    loadLeagues();
    loadTopPredictions();
});

// ========== LOAD LEAGUES ==========
async function loadLeagues() {
    try {
        const response = await fetch('/api/leagues');
        leaguesData = await response.json();

        const select = document.getElementById('league-select');
        select.innerHTML = '<option value="">Sélectionner un championnat...</option>';

        for (const [id, league] of Object.entries(leaguesData)) {
            select.innerHTML += `<option value="${id}">${league.name} (${league.country})</option>`;
        }
    } catch (e) {
        console.error('Erreur chargement leagues:', e);
    }
}

// ========== LOAD TEAMS ==========
async function loadTeams() {
    const leagueId = document.getElementById('league-select').value;
    if (!leagueId) return;

    currentLeague = leagueId;

    try {
        const response = await fetch(`/api/teams/${leagueId}`);
        const teams = await response.json();

        const homeSelect = document.getElementById('home-team');
        const awaySelect = document.getElementById('away-team');

        homeSelect.innerHTML = '<option value="">Sélectionner...</option>';
        awaySelect.innerHTML = '<option value="">Sélectionner...</option>';

        teams.forEach(team => {
            homeSelect.innerHTML += `<option value="${team}">${team}</option>`;
            awaySelect.innerHTML += `<option value="${team}">${team}</option>`;
        });
    } catch (e) {
        console.error('Erreur chargement teams:', e);
    }
}

// ========== PREDICT MATCH ==========
async function predictMatch() {
    const homeTeam = document.getElementById('home-team').value;
    const awayTeam = document.getElementById('away-team').value;
    const leagueId = document.getElementById('league-select').value;

    if (!homeTeam || !awayTeam) {
        alert('Veuillez sélectionner les deux équipes');
        return;
    }

    if (homeTeam === awayTeam) {
        alert('Les deux équipes doivent être différentes');
        return;
    }

    const btn = document.querySelector('.btn-primary');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyse en cours...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ home_team: homeTeam, away_team: awayTeam, league_id: leagueId })
        });

        const data = await response.json();
        displayPrediction(data);

    } catch (e) {
        console.error('Erreur prédiction:', e);
        alert('Erreur lors de l'analyse');
    } finally {
        btn.innerHTML = '<i class="fas fa-magic"></i> Analyser le Match';
        btn.disabled = false;
    }
}

// ========== DISPLAY PREDICTION ==========
function displayPrediction(data) {
    const resultDiv = document.getElementById('prediction-result');
    const match = data.match;
    const pred = data.prediction;

    const getBarClass = (val) => val >= 60 ? 'high' : (val >= 40 ? 'medium' : 'low');

    resultDiv.innerHTML = `
        <div class="card">
            <div class="result-header">
                <h2><i class="fas fa-chart-bar"></i> Résultat de l'Analyse</h2>
                <span class="match-time"><i class="fas fa-calendar"></i> ${match.match_date}</span>
            </div>

            <div class="match-display">
                <div class="team-display">
                    <div class="team-avatar" style="width:64px;height:64px;background:linear-gradient(135deg,#6366f1,#4f46e5);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800;color:white;">${match.home_team.substring(0,2).toUpperCase()}</div>
                    <div class="team-name">${match.home_team}</div>
                    <div class="team-form">Forme: ${match.home_form}/100</div>
                </div>
                <div class="score-prediction">
                    <div class="predicted-score">${pred.expected_goals}</div>
                    <div class="expected-goals">Buts attendus</div>
                </div>
                <div class="team-display">
                    <div class="team-avatar" style="width:64px;height:64px;background:linear-gradient(135deg,#ec4899,#db2777);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800;color:white;">${match.away_team.substring(0,2).toUpperCase()}</div>
                    <div class="team-name">${match.away_team}</div>
                    <div class="team-form">Forme: ${match.away_form}/100</div>
                </div>
            </div>

            <div class="probabilities-grid">
                <div class="prob-card">
                    <h4><i class="fas fa-trophy"></i> 1X2</h4>
                    ${Object.entries(pred['1x2']).map(([k,v]) => `
                        <div class="prob-item">
                            <span class="prob-label">${k === '1' ? 'Domicile' : (k === 'X' ? 'Nul' : 'Extérieur')}</span>
                            <span class="prob-value" style="color:${v >= 50 ? 'var(--success)' : (v >= 30 ? 'var(--warning)' : 'var(--danger)')}">${v}%</span>
                        </div>
                        <div class="prob-bar-bg">
                            <div class="prob-bar-fill ${getBarClass(v)}" style="width:${v}%"></div>
                        </div>
                    `).join('')}
                </div>

                <div class="prob-card">
                    <h4><i class="fas fa-arrow-up"></i> Over/Under 2.5</h4>
                    <div class="prob-item">
                        <span class="prob-label">Over 2.5</span>
                        <span class="prob-value" style="color:${pred.over_under.over_2_5 >= 50 ? 'var(--success)' : 'var(--danger)'}">${pred.over_under.over_2_5}%</span>
                    </div>
                    <div class="prob-bar-bg">
                        <div class="prob-bar-fill ${getBarClass(pred.over_under.over_2_5)}" style="width:${pred.over_under.over_2_5}%"></div>
                    </div>
                    <div class="prob-item" style="margin-top:12px;">
                        <span class="prob-label">Under 2.5</span>
                        <span class="prob-value" style="color:${pred.over_under.under_2_5 >= 50 ? 'var(--success)' : 'var(--danger)'}">${pred.over_under.under_2_5}%</span>
                    </div>
                    <div class="prob-bar-bg">
                        <div class="prob-bar-fill ${getBarClass(pred.over_under.under_2_5)}" style="width:${pred.over_under.under_2_5}%"></div>
                    </div>
                </div>

                <div class="prob-card">
                    <h4><i class="fas fa-exchange-alt"></i> BTTS</h4>
                    <div class="prob-item">
                        <span class="prob-label">Oui</span>
                        <span class="prob-value" style="color:${pred.btts.yes >= 50 ? 'var(--success)' : 'var(--danger)'}">${pred.btts.yes}%</span>
                    </div>
                    <div class="prob-bar-bg">
                        <div class="prob-bar-fill ${getBarClass(pred.btts.yes)}" style="width:${pred.btts.yes}%"></div>
                    </div>
                    <div class="prob-item" style="margin-top:12px;">
                        <span class="prob-label">Non</span>
                        <span class="prob-value" style="color:${pred.btts.no >= 50 ? 'var(--success)' : 'var(--danger)'}">${pred.btts.no}%</span>
                    </div>
                    <div class="prob-bar-bg">
                        <div class="prob-bar-fill ${getBarClass(pred.btts.no)}" style="width:${pred.btts.no}%"></div>
                    </div>
                </div>
            </div>

            <div class="best-pick-card">
                <h3><i class="fas fa-star"></i> Meilleure Prédiction</h3>
                <div class="pick-value">${pred.best_pick}</div>
                <div class="pick-confidence">Confiance: ${pred.confidence}%</div>
                <span class="risk-tag" style="background:${pred.risk_color}40;color:${pred.risk_color};border:1px solid ${pred.risk_color}">
                    <i class="fas fa-shield-alt"></i> ${pred.risk_level}
                </span>
            </div>

            <div class="stats-comparison">
                <div class="stats-col left">
                    <div class="stat-row"><span class="value">${match.home_avg_goals_scored}</span></div>
                    <div class="stat-row"><span class="value">${match.home_avg_goals_conceded}</span></div>
                    <div class="stat-row"><span class="value">${match.home_possession}%</span></div>
                    <div class="stat-row"><span class="value">${match.home_shots_per_game}</span></div>
                </div>
                <div class="stats-col center">
                    <div class="stat-row"><span class="label">Buts Marqués</span></div>
                    <div class="stat-row"><span class="label">Buts Encaissés</span></div>
                    <div class="stat-row"><span class="label">Possession</span></div>
                    <div class="stat-row"><span class="label">Tirs/Match</span></div>
                </div>
                <div class="stats-col right">
                    <div class="stat-row"><span class="value">${match.away_avg_goals_scored}</span></div>
                    <div class="stat-row"><span class="value">${match.away_avg_goals_conceded}</span></div>
                    <div class="stat-row"><span class="value">${match.away_possession}%</span></div>
                    <div class="stat-row"><span class="value">${match.away_shots_per_game}</span></div>
                </div>
            </div>

            <div class="h2h-section">
                <div class="h2h-title"><i class="fas fa-history"></i> Head-to-Head (5 derniers)</div>
                <div class="h2h-list">
                    ${match.h2h.map(h => `
                        <div class="h2h-item">
                            <span class="h2h-date">${h.date}</span>
                            <span>${h.home} <strong style="color:var(--accent-light)">${h.score}</strong> ${h.away}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="last-matches-grid">
                <div class="last-matches-col">
                    <h4><i class="fas fa-home"></i> ${match.home_team} - 5 derniers</h4>
                    ${match.home_last_5.map(m => `
                        <div class="last-match-item">
                            <span>${m.opponent.substring(0,15)}${m.opponent.length>15?'...':''}</span>
                            <span><span class="result ${m.result}">${m.result}</span> ${m.score}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="last-matches-col">
                    <h4><i class="fas fa-plane"></i> ${match.away_team} - 5 derniers</h4>
                    ${match.away_last_5.map(m => `
                        <div class="last-match-item">
                            <span>${m.opponent.substring(0,15)}${m.opponent.length>15?'...':''}</span>
                            <span><span class="result ${m.result}">${m.result}</span> ${m.score}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;

    resultDiv.style.display = 'block';
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

// ========== LOAD TODAY MATCHES ==========
async function loadTodayMatches() {
    const container = document.getElementById('today-matches');
    container.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Chargement...</div>';

    try {
        const response = await fetch('/api/today-matches');
        const matches = await response.json();

        container.innerHTML = matches.map(m => createMatchCard(m)).join('');
    } catch (e) {
        container.innerHTML = '<div class="loading">Erreur de chargement</div>';
    }
}

// ========== LOAD TOP PREDICTIONS ==========
async function loadTopPredictions() {
    const container = document.getElementById('top-predictions');
    if (!container) return;

    try {
        const response = await fetch('/api/today-matches');
        const matches = await response.json();

        // Trier par confiance
        const sorted = matches.sort((a, b) => b.prediction.confidence - a.prediction.confidence).slice(0, 5);

        container.innerHTML = sorted.map(m => `
            <div class="prediction-item" onclick="loadMatchDetail('${m.match.home_team}', '${m.match.away_team}', '${Object.keys(leaguesData).find(k => leaguesData[k].name === m.match.league) || 'premier-league'}')">
                <div class="prediction-teams">
                    <div class="team-badge">
                        <div style="width:32px;height:32px;background:linear-gradient(135deg,#6366f1,#4f46e5);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white;">${m.match.home_team.substring(0,2).toUpperCase()}</div>
                        <span>${m.match.home_team}</span>
                    </div>
                    <span class="vs-small">VS</span>
                    <div class="team-badge">
                        <div style="width:32px;height:32px;background:linear-gradient(135deg,#ec4899,#db2777);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white;">${m.match.away_team.substring(0,2).toUpperCase()}</div>
                        <span>${m.match.away_team}</span>
                    </div>
                </div>
                <div class="prediction-meta">
                    <span class="league-tag">${m.match.league}</span>
                    <span class="best-pick">${m.prediction.best_pick}</span>
                    <span class="confidence-badge ${m.prediction.risk_level.toLowerCase()}">${m.prediction.confidence}%</span>
                </div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Erreur top predictions:', e);
    }
}

// ========== CREATE MATCH CARD ==========
function createMatchCard(data) {
    const m = data.match;
    const p = data.prediction;

    return `
        <div class="match-card">
            <div class="match-card-header">
                <span class="match-league">${m.league}</span>
                <span class="match-time">${m.match_date.split(' ')[1] || '20:00'}</span>
            </div>
            <div class="match-teams-row">
                <div class="match-team">
                    <div style="width:28px;height:28px;background:linear-gradient(135deg,#6366f1,#4f46e5);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:white;">${m.home_team.substring(0,2).toUpperCase()}</div>
                    ${m.home_team}
                </div>
                <span style="color:var(--text-secondary);font-weight:700;">VS</span>
                <div class="match-team">
                    <div style="width:28px;height:28px;background:linear-gradient(135deg,#ec4899,#db2777);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:white;">${m.away_team.substring(0,2).toUpperCase()}</div>
                    ${m.away_team}
                </div>
            </div>
            <div class="match-prediction-row">
                <span class="match-prediction"><i class="fas fa-star"></i> ${p.best_pick}</span>
                <span class="confidence-badge ${p.risk_level.toLowerCase()}">${p.confidence}% ${p.risk_level}</span>
            </div>
        </div>
    `;
}

// ========== LOAD MATCH DETAIL ==========
async function loadMatchDetail(home, away, league) {
    showSection('predictor');
    document.getElementById('league-select').value = league;
    await loadTeams();
    document.getElementById('home-team').value = home;
    document.getElementById('away-team').value = away;
    predictMatch();
}
