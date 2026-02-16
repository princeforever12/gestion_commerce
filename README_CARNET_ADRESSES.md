# 📒 Carnet d'adresses en Python (Projet pédagogique)

Ce mini-projet répond exactement à la consigne:

> Créer un carnet d'adresses avec un dictionnaire où les clés sont les noms et les valeurs sont des tuples `(telephone, email)`, avec des fonctions pour ajouter, supprimer, rechercher et afficher les contacts.

Le code est implémenté dans `pharmacy_pos/carnet_adresses.py`.

---

## ✅ Structure de données

Le carnet est un dictionnaire Python:

```python
carnet = {
    "Alice": ("06 11 22 33 44", "alice@example.com"),
    "Bob": ("+33 6 99 88 77 66", "bob@example.com"),
}
```

- **clé**: nom (`str`)
- **valeur**: tuple `(telephone, email)`

---

## 🧩 Fonctions disponibles

### 1) `ajouter_contact(carnet, nom, telephone, email)`
Ajoute un nouveau contact ou met à jour un contact existant.

### 2) `supprimer_contact(carnet, nom)`
Supprime un contact et retourne:
- `True` si le contact existait,
- `False` sinon.

### 3) `rechercher_contact(carnet, nom)`
Retourne `(telephone, email)` si le contact existe, sinon `None`.

### 4) `afficher_tous_les_contacts(carnet)`
Retourne la liste des contacts formatés en texte, triés alphabétiquement.

---

## 🛡️ Validation (bonus pour une version "propre")

Pour éviter les données invalides:
- nom non vide,
- format téléphone tolérant (`0-9`, `+`, espaces, `(` `)` `-`),
- format email basique valide.

Si une valeur est invalide, une `ValueError` est levée.

---

## ▶️ Démonstration rapide

Exécuter:

```bash
python -m pharmacy_pos.carnet_adresses
```

Le script affiche une démonstration complète:
1. ajout de contacts,
2. affichage,
3. recherche,
4. suppression,
5. affichage final.

---

## 🧪 Tests

Lancer les tests dédiés:

```bash
python -m pytest -q tests/test_carnet_adresses.py
```

Les tests vérifient:
- ajout + recherche,
- suppression,
- tri d'affichage,
- validations d'entrées invalides.

---

## 💡 Pourquoi cette version peut impressionner

- Respect strict de la consigne de base.
- Code propre, typé et documenté.
- Gestion d'erreurs réaliste.
- Tests automatisés pour prouver le bon fonctionnement.
- Démo exécutable directement en ligne de commande.

