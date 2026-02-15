#!/usr/bin/env bash
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Erreur: ce script doit être lancé dans un dépôt Git." >&2
  exit 1
fi

BRANCH="$(git branch --show-current)"
if [[ -z "$BRANCH" ]]; then
  echo "Erreur: impossible de déterminer la branche courante." >&2
  exit 1
fi

if [[ "$BRANCH" == "main" ]]; then
  echo "Tu es déjà sur main. Passe sur ta branche de PR avant d'exécuter ce script." >&2
  exit 1
fi

echo "Branche courante: $BRANCH"
echo "1) fetch origin"
git fetch origin

echo "2) merge origin/main dans $BRANCH"
if git merge origin/main; then
  echo "Merge réussi sans conflit."
  echo "3) push"
  git push
  echo "Terminé ✅"
else
  echo "Conflits détectés ⚠️"
  echo "Résous les fichiers en conflit, puis exécute:"
  echo "  git add <fichiers> && git commit -m 'fix: resolve conflicts with main' && git push"
  exit 2
fi
