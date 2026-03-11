# Notes de visibilité des changements (GitHub)

Si vous ne voyez pas les changements dans votre dépôt GitHub, vérifiez ces points :

1. **Branche locale**
   - Les changements ont été faits dans une branche de travail locale.
   - Vérifiez la branche active :
     ```bash
     git branch --show-current
     ```

2. **Push vers votre dépôt distant**
   - Ajoutez votre remote si nécessaire :
     ```bash
     git remote add origin <URL_DU_REPO_GITHUB>
     ```
   - Puis poussez la branche voulue :
     ```bash
     git push -u origin <branche_locale>
     ```

3. **Si vous voulez voir les changements sur `main`**
   - Fusionnez la branche de travail dans `main`, puis poussez `main`.

4. **Déploiement GitHub Pages**
   - Le workflow de déploiement se lance sur `main`/`master`.
   - Donc tant que ces branches ne reçoivent pas les commits, la page ne se mettra pas à jour.

Fichiers UI attendus après push :
- `index.html`
- `web/app.js`
- `web/styles.css`
- `.github/workflows/deploy-pages.yml`
