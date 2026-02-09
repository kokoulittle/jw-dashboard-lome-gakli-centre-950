# JW Dashboard – Préposés à l’Accueil

## Objectifs du projet

Ce projet fournit un tableau de bord interactif permettant de :

- consulter les préposés à l’accueil par semaine,
- exporter des PDF hebdomadaires officiels,
- garantir la traçabilité et la stabilité du planning annuel.

Le système repose sur un principe central :

> **Le planning annuel est figé et versionné comme source de vérité.**

---

## Architecture et principes clés

### Séparation des responsabilités

| Composant                               | Rôle                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| attendance_program.py                   | Génération initiale du planning (outil interne, non déployé) |
| Random_Attendant_Crew_Schedule_2026.csv | Source de vérité annuelle                                      |
| dashboard.py                            | Visualisation, filtres, exports PDF                              |
| Docker                                  | Déploiement lecture seule                                       |

---

## Structure du projet

```text
jw-dashboard/
├── attendance_program.py        # Génération initiale (ONE-SHOT)
├── dashboard.py                 # Application Dash
├── requirements.txt
├── Dockerfile
├── README.md
├── .gitignore

├── assets/
│   └── JW_Logo.png

├── data/
│   └── Random_Attendant_Crew_Schedule_2026.csv   # SOURCE DE VÉRITÉ

├── exports/
│   └── pdf/
```
