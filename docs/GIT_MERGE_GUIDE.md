# Guide rapide — mettre à jour la branche `main` sans blocage

Si la PR affiche **"This branch has conflicts that must be resolved"**, suis cette méthode locale.

## 1) Se placer sur ta branche de travail
```bash
git checkout <ta-branche>
```

## 2) Récupérer l'état distant
```bash
git fetch origin
```

## 3) Fusionner `main` dans ta branche
```bash
git merge origin/main
```

## 4) Résoudre les conflits
Dans chaque fichier en conflit, supprime les marqueurs :
- `<<<<<<< HEAD`
- `=======`
- `>>>>>>> origin/main`

Puis valide :
```bash
git add <fichiers_resolus>
git commit -m "fix: resolve conflicts with main"
```

## 5) Pousser la branche
```bash
git push
```

La PR sera mise à jour automatiquement, et le bouton **Merge pull request** redeviendra disponible.

---

## Option rapide (garder ta version de fichier)
Si tu veux garder la version de ta branche sur un fichier donné :
```bash
git checkout --ours <fichier>
git add <fichier>
git commit -m "fix: keep branch version for conflict"
git push
```

## Option inverse (garder la version de `main`)
```bash
git checkout --theirs <fichier>
git add <fichier>
git commit -m "fix: keep main version for conflict"
git push
```
