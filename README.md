# ⚽ Football Analyzer Pro

Application d'analyse et de prédiction de matchs de football avec moteur Machine Learning intégré.

## 🚀 Déploiement sur Render (Gratuit)

### Étape 1: Créer un compte Render
1. Va sur [render.com](https://render.com)
2. Clique sur "Get Started for Free"
3. Inscris-toi avec GitHub, Google, ou email

### Étape 2: Créer un nouveau Web Service
1. Dans le dashboard Render, clique sur **"New +"** → **"Web Service"**
2. Choisis **"Build and deploy from a Git repository"**
3. Connecte ton compte GitHub et crée un nouveau repo
4. Upload ces fichiers dans le repo

### Étape 3: Configuration
- **Name**: `football-analyzer` (ou ce que tu veux)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Plan**: Free

### Étape 4: Deploy
Clique sur **"Create Web Service"**
Render va build et deploy automatiquement.

### Étape 5: Ton URL
Une fois déployé, Render te donne une URL du type:
```
https://football-analyzer-xxx.onrender.com
```

---

## 📁 Structure du Projet

```
football-analyzer/
├── app.py              # Backend Flask + ML Engine
├── requirements.txt    # Dépendances Python
├── render.yaml         # Config Render
├── Procfile            # Commande de démarrage
├── templates/
│   └── index.html      # Frontend
├── static/
│   ├── css/
│   │   └── style.css   # Styles
│   └── js/
│       └── app.js      # Logique frontend
```

---

## 🔧 Fonctionnalités

- ✅ **Dashboard** avec statistiques en temps réel
- ✅ **Prédiction ML** 1X2, Over/Under 2.5, BTTS
- ✅ **Analyse complète**: Forme, H2H, stats comparatives
- ✅ **Matchs du jour** avec filtres par niveau de risque
- ✅ **4 niveaux de risque**: SAFE, MODERATE, RISKY
- ✅ **UI Dark/Modern** responsive mobile
- ✅ **6 championnats**: PL, La Liga, Serie A, Bundesliga, Ligue 1, UCL

---

## 🧠 Algorithme ML

Le moteur de prédiction utilise:
- Forme des équipes (0-100)
- Moyenne de buts marqués/encaissés
- Possession moyenne
- Tirs par match
- Head-to-head historique
- Derniers résultats (5 matchs)

Formule de calcul de la force:
```
Force = (Forme × 0.3) + (ButsMarqués × 15) + ((2-ButsEncaissés) × 10) + (Possession × 0.3)
```

---

## 📝 Notes

- Les données actuelles sont **simulées** mais réalistes
- Pour du vrai scraping, remplace `generate_match_data()` par des appels à Flashscore/SofaScore
- Ajoute `requests` + `beautifulsoup4` pour le scraping réel
- Le modèle peut être amélioré avec scikit-learn (Random Forest, XGBoost)

---

## 🛠️ Stack Technique

- **Backend**: Python, Flask, Gunicorn
- **Frontend**: HTML5, CSS3, Vanilla JS
- **ML**: Algorithme probabiliste custom
- **Hébergement**: Render (Free Tier)

---

Made with ⚽ by Football Analyzer Pro
