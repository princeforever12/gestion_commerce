# Gestion de caisse pharmacie (MVP Python + Tkinter)

Ce dépôt contient un **MVP fonctionnel** pour démarrer un projet de gestion de caisse de pharmacie avec une interface graphique Tkinter.

## Fonctionnalités incluses
- Initialisation DB SQLite.
- Utilisateur admin par défaut (`admin` / `admin123`).
- Interface de connexion.
- UI modernisée: tables zébrées et barre d’astuce en dashboard.
- Interface caisse (ajout de lignes + validation de vente).
- Recherche produit en caisse (nom / code-barres).
- Interface stock (création produit, ajout de lot, listing stock).
- Gestion des rôles: admin / caissier / pharmacien.
- Onglet admin pour créer des utilisateurs.
- Vente avec décrémentation FIFO du stock.
- Rapport du jour (total HT/TVA/TTC) et top produits.
- Historique des ventes avec détail par ticket.
- Annulation ticket et retour partiel depuis l'historique.
- Export ticket texte (TXT) depuis l'historique.
- Export CSV des rapports (ventes, top produits, stock, péremption).
- Alerte de stock bas.
- Alerte de péremption (lots <= 90 jours).
- Exclusion des lots expirés lors des ventes (FIFO sur lots valides).
- Contrôle ordonnance pour produits sensibles (validation à la caisse).

## Lancement
```bash
python app.py
```

## Structure
- `pharmacy_pos/database.py` : schéma SQLite + helpers transactionnels.
- `pharmacy_pos/services/` : logique métier par module.
- `pharmacy_pos/ui/app_tk.py` : interface Tkinter (login + tabs caisse/stock/rapports/historique).
- `tests/` : tests unitaires des flux métier.

## Notes
- La couche métier est découplée de l'UI, ce qui facilite le passage futur vers FastAPI/Streamlit si besoin.


## Workflow Git (anti-conflits)
- Guide détaillé: `docs/GIT_MERGE_GUIDE.md`
- Script d'aide (depuis ta branche de PR):
```bash
./tools/sync_main.sh
```
