# Trading Economics Discord Bot

Poste automatiquement les événements du calendrier économique de [Trading Economics](https://tradingeconomics.com/calendar) dans le salon Discord correspondant à leur niveau d'importance (⭐ / ⭐⭐ / ⭐⭐⭐), avec :
- un **rappel** ~30-60 min avant chaque publication à venir,
- une **alerte** dès que le résultat (Actual) est publié, comparé au consensus/prévision.

Données : scrapées directement depuis la page publique du calendrier (pas d'API payante nécessaire — le compte "guest" gratuit de l'API officielle a été supprimé). Même technique que le bot FedWatch : `curl_cffi` avec imitation TLS de Chrome pour éviter le blocage anti-bot.

Hébergement : 100% gratuit via GitHub Actions (cron toutes les 5 min), dépôt public. Réutilise le même bot Discord que le projet `fedwatch-discord-bot` (même token).

## Ce que tu dois faire

### 1. Vérifier les permissions du bot sur les 3 salons

Le bot Discord existant ("FedWatch Bot") doit pouvoir envoyer des messages avec embeds dans `#infos-⭐`, `#infos-⭐⭐`, `#infos-⭐⭐⭐`. Si ces salons ont des permissions spécifiques qui bloquent le bot (override de salon), ajuste-les dans Discord : clic droit sur le salon → Modifier le salon → Permissions → ajoute le rôle du bot avec "Envoyer des messages" + "Intégrer des liens".

### 2. Récupérer les 3 ID de salon

Mode développeur déjà activé (fait pour le bot FedWatch). Clic droit sur chaque salon → **Copier l'identifiant du salon** :
- `#infos-⭐` → ID pour `DISCORD_CHANNEL_1STAR`.     1543736947510616128
- `#infos-⭐⭐` → ID pour `DISCORD_CHANNEL_2STAR`.    1543737014623670312
- `#infos-⭐⭐⭐` → ID pour `DISCORD_CHANNEL_3STAR`.   1543737143715696740

### 3. Créer le dépôt GitHub et pousser le code

```bash
git init
git add .
git commit -m "Initial commit: Trading Economics Discord bot"
gh repo create trading-economics-discord-bot --public --source=. --push
```

### 4. Ajouter les secrets GitHub

Sur la page du dépôt : **Settings → Secrets and variables → Actions → New repository secret**, ajoute :
- `DISCORD_BOT_TOKEN` = le même token que le bot FedWatch
- `DISCORD_CHANNEL_1STAR`, `DISCORD_CHANNEL_2STAR`, `DISCORD_CHANNEL_3STAR` = les 3 ID récupérés à l'étape 2

### 5. Activer les droits d'écriture du workflow

**Settings → Actions → General → Workflow permissions → "Read and write permissions"** → Save. (Nécessaire pour que le bot puisse committer `state.json` après chaque run — leçon du bot FedWatch.)

### 6. Lancer le premier run

Onglet **Actions** → workflow **"Post Trading Economics calendar events"** → **Run workflow**.

## Comment ça marche

- Toutes les 5 minutes, le bot récupère la page publique du calendrier (`?g=world`, ~99 pays), filtre sur une liste de ~69 pays pertinents pour le FX (`src/countries.py`, facile à ajuster).
- Pour chaque événement dont l'heure prévue tombe dans l'heure à venir et qui n'a pas encore de résultat : poste un rappel.
- Pour chaque événement dont le résultat vient d'être publié : poste une alerte avec Actual vs Prévision vs Précédent.
- `state.json` garde la trace de ce qui a déjà été posté (évite les doublons), avec purge automatique des entrées de plus de 3 jours.

## Vérifier que tout fonctionne

- Les messages doivent apparaître dans le bon salon selon le nombre d'étoiles.
- Si le run échoue, regarde les logs dans l'onglet Actions.
- Un doublon ne doit jamais apparaître pour un même événement (dédoublonnage via `state.json`).
