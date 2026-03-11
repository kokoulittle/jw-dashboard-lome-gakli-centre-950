# JW Dashboard – Préposés à l’Accueil

## Objectifs du projet

Ce projet fournit un tableau de bord interactif permettant de :

- consulter les préposés à l’accueil par semaine,
- exporter des PDF hebdomadaires officiels,
- garantir la traçabilité et la stabilité du planning annuel.

Le système repose sur un principe central :

> **Le planning annuel est figé et versionné comme source de vérité.**

---

## Déploiement sur GitHub Pages (UI interactive)

Le dépôt embarque maintenant une UI 100% front-end (`index.html` + `web/app.js`) déployée automatiquement sur GitHub Pages via GitHub Actions.

### Ce que cela change

- plus besoin de Railway pour l'interface utilisateur ;
- la sélection de semaine reste interactive dans le navigateur ;
- l’export PDF est généré côté client (dans le navigateur).

### Activer GitHub Pages

1. Pousser le dépôt sur GitHub.
2. Aller dans **Settings → Pages** et choisir **GitHub Actions** comme source.
3. Vérifier que la branche de déploiement est `main` (ou `master`) dans le workflow `.github/workflows/deploy-pages.yml`.
4. À chaque push sur cette branche, le site est redéployé automatiquement.
5. Le workflow publie uniquement les fichiers statiques nécessaires (`index.html`, `assets/`, `data/`, `web/`).

---

> En cas de doute sur la visibilité des commits dans GitHub, voir `DEPLOYMENT_NOTES.md`.

## Architecture et principes clés

### Séparation des responsabilités

| Composant                               | Rôle                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| attendance_program.py                   | Génération initiale du planning (outil interne, non déployé) |
| Random_Attendant_Crew_Schedule_2026.csv | Source de vérité annuelle                                      |
| dashboard.py                            | Visualisation/exports côté Python (historique)                  |
| index.html + web/app.js                 | UI GitHub Pages (production statique interactive)               |
| GitHub Actions                          | Déploiement automatique sur Pages                               |

---

## Structure du projet

```text
jw-dashboard/
├── attendance_program.py
├── dashboard.py
├── index.html                      # UI statique pour GitHub Pages
├── web/
│   ├── app.js
│   └── styles.css
├── .github/workflows/
│   └── deploy-pages.yml
├── assets/
│   └── JW_Logo.png
├── data/
│   └── Random_Attendant_Crew_Schedule_2026.csv   # SOURCE DE VÉRITÉ
└── exports/
    └── pdf/
```
