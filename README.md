# Sync Garmin → Cockpit (gratuit, via GitHub Actions)

Récupère automatiquement tes activités Garmin 2x/jour et les écrit dans
`data/garmin-sessions.json`, que l'app `cockpit-sport.html` va lire directement.

⚠️ Cette lib (`garminconnect`/`garth`) n'est pas l'API officielle Garmin — elle
imite la connexion de l'app mobile. Usage personnel très répandu, mais pas
formellement "autorisé" par les CGU Garmin. À toi de voir.

## Étapes (15 min, une seule fois)

### 1. Crée un repo GitHub
- Nouveau repo, **public** (nécessaire pour que l'app web lise le JSON sans authentification — il ne contiendra que tes séances, jamais ton mot de passe)
- Uploade-y tout le contenu de ce dossier

### 2. Génère tes jetons de connexion, EN LOCAL sur ton ordi
```bash
pip install garminconnect
python generate_tokens.py
```
Entre ton email/mot de passe Garmin (et le code MFA si tu l'as activé).
Le script imprime un long bloc en base64 à la fin.

**Jamais ton mot de passe n'est envoyé à GitHub** — seulement ce jeton de session.

### 3. Ajoute le secret dans GitHub
Repo → **Settings → Secrets and variables → Actions → New repository secret**
- Nom : `GARMIN_TOKENS_B64`
- Valeur : colle le bloc base64 généré à l'étape 2

### 4. Active le workflow
Onglet **Actions** du repo → autorise les workflows si demandé → tu peux
lancer `Sync Garmin activities` manuellement (bouton "Run workflow") pour
tester tout de suite, sans attendre le cron.

### 5. Branche l'app dessus
Dans `cockpit-sport.html`, ouvre les Réglages (icône ⚙️ en haut) et colle
l'URL brute de ton fichier JSON, du style :
```
https://raw.githubusercontent.com/TON_USER/TON_REPO/main/data/garmin-sessions.json
```

## Si la synchro casse un jour
Garmin change parfois son système de connexion, ce qui peut invalider les
jetons. Il suffit de relancer `generate_tokens.py` en local et de remettre à
jour le secret `GARMIN_TOKENS_B64`.
