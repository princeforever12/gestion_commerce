# Gestion de caisse pharmacie (MVP Python + Tkinter)

Ce dépôt contient un **MVP fonctionnel** pour démarrer un projet de gestion de caisse de pharmacie avec une interface graphique Tkinter.

## Fonctionnalités incluses
- Initialisation DB SQLite.
- Utilisateur admin par défaut (`admin` / `admin123`).
- Interface de connexion.
- Interface caisse (ajout de lignes + validation de vente).
- Interface stock (création produit, ajout de lot, listing stock).
- Gestion des rôles: admin / caissier / pharmacien.
- Onglet admin pour créer des utilisateurs.
- Vente avec décrémentation FIFO du stock.
- Rapport du jour (total HT/TVA/TTC) et top produits.
- Alerte de stock bas.
- Alerte de péremption (lots <= 90 jours).
- Exclusion des lots expirés lors des ventes (FIFO sur lots valides).

## Lancement
```bash
python app.py
```

## Structure
- `pharmacy_pos/database.py` : schéma SQLite + helpers transactionnels.
- `pharmacy_pos/services/` : logique métier par module.
- `pharmacy_pos/ui/app_tk.py` : interface Tkinter (login + tabs caisse/stock/rapports).
- `tests/` : tests unitaires des flux métier.

## Notes
- La couche métier est découplée de l'UI, ce qui facilite le passage futur vers FastAPI/Streamlit si besoin.


## Workflow Git (anti-conflits)
- Guide détaillé: `docs/GIT_MERGE_GUIDE.md`
- Script d'aide (depuis ta branche de PR):
```bash
./tools/sync_main.sh
```
