# Projet complet Python — Gestion de caisse pour une pharmacie

## 1) Objectif du projet
Créer une application de **gestion de caisse pour pharmacie** qui permet de :
- vendre des médicaments et produits de parapharmacie ;
- gérer le stock avec alertes de seuil minimal ;
- suivre les dates de péremption ;
- éditer des tickets/factures ;
- produire des rapports (journal de caisse, ventes par produit, bénéfice, etc.).

---

## 2) Fonctionnalités principales (MVP)

### A. Authentification et rôles
- Connexion utilisateur (`admin`, `caissier`, `pharmacien`).
- Permissions :
  - `admin` : configuration, gestion utilisateurs, rapports complets.
  - `caissier` : vente, retour, consultation stock.
  - `pharmacien` : validation de certaines ventes si nécessaire.

### B. Catalogue produits
- CRUD produit (nom, catégorie, code-barres, prix achat, prix vente, TVA).
- Gestion lots (`lot`, `date_expiration`, `quantite_lot`).
- Indicateur : produit **prescription obligatoire** (oui/non).

### C. Stock
- Entrée de stock (approvisionnement fournisseur).
- Sortie automatique lors des ventes.
- Alerte stock bas.
- Alerte péremption (ex: < 90 jours).

### D. Caisse et ventes
- Ajout produits au panier (scan code-barres ou recherche).
- Calcul total, réduction, TVA, montant rendu.
- Paiements multiples : espèces, carte, mobile money.
- Impression ticket (texte/PDF).

### E. Retours / Annulations
- Retour produit (avec contrôle délai et état).
- Historique des annulations avec motif.

### F. Rapports
- Chiffre d'affaires journalier/mensuel.
- Produits les plus vendus.
- Marge brute estimée.
- Rapport stock (rupture, péremption, valeur de stock).

---

## 3) Stack technique recommandée

### Option 1 (la plus simple pour un projet scolaire)
- **Backend + UI** : Python + `Tkinter`.
- **Base de données** : `SQLite`.
- **PDF ticket/rapport** : `reportlab` ou `fpdf2`.
- **Graphiques** : `matplotlib`.

### Option 2 (plus moderne, meilleur pour portfolio)
- **Backend API** : `FastAPI`.
- **Frontend** : `Streamlit` (ou web HTML/CSS simple).
- **DB** : `SQLite` en dev puis `PostgreSQL`.
- **ORM** : `SQLAlchemy`.

👉 Si ton prof veut un projet "classique Python", prends **Option 1**.

---

## 4) Modèle de base de données (minimum)

### Tables
1. `users`
   - `id`, `username`, `password_hash`, `role`, `created_at`
2. `categories`
   - `id`, `name`
3. `products`
   - `id`, `name`, `barcode`, `category_id`, `buy_price`, `sell_price`, `tva`, `requires_prescription`, `min_stock`
4. `batches`
   - `id`, `product_id`, `batch_number`, `expiry_date`, `quantity`
5. `sales`
   - `id`, `cashier_id`, `total_ht`, `total_tva`, `total_ttc`, `payment_method`, `created_at`
6. `sale_items`
   - `id`, `sale_id`, `product_id`, `batch_id`, `quantity`, `unit_price`, `line_total`
7. `stock_movements`
   - `id`, `product_id`, `type` (IN/OUT/ADJUST), `quantity`, `reason`, `created_at`
8. `returns`
   - `id`, `sale_item_id`, `quantity`, `reason`, `created_at`

---

## 5) Architecture projet (propre et notée)

```text
pharmacy_pos/
├─ app.py
├─ config.py
├─ requirements.txt
├─ database/
│  ├─ db.py
│  ├─ models.py
│  └─ seed.py
├─ services/
│  ├─ auth_service.py
│  ├─ product_service.py
│  ├─ stock_service.py
│  ├─ sales_service.py
│  └─ report_service.py
├─ ui/
│  ├─ login_view.py
│  ├─ dashboard_view.py
│  ├─ pos_view.py
│  ├─ stock_view.py
│  └─ reports_view.py
├─ utils/
│  ├─ validators.py
│  ├─ barcode.py
│  └─ pdf_export.py
└─ tests/
   ├─ test_sales.py
   ├─ test_stock.py
   └─ test_reports.py
```

---

## 6) Plan de réalisation (2 à 4 semaines)

### Semaine 1
- Mise en place projet + base SQLite.
- Authentification + gestion produits.

### Semaine 2
- Module caisse complet (panier, paiement, ticket).
- Mouvements de stock automatiques.

### Semaine 3
- Rapports + alertes stock/péremption.
- Retours et annulations.

### Semaine 4 (bonus)
- Interface améliorée.
- Export Excel/PDF.
- Tests unitaires + démo propre.

---

## 7) Critères d'évaluation (ce qui impressionne un prof)
- Code modulaire (séparation UI / logique / DB).
- Validation des entrées (pas de valeurs négatives, dates valides, etc.).
- Gestion des erreurs propre.
- Données de démonstration réalistes.
- Présentation avec scénario complet :
  1) ajout produit,
  2) approvisionnement,
  3) vente,
  4) impression ticket,
  5) consultation rapport du jour.

---

## 8) Bonus "niveau pro"
- Journal d'audit (`qui a fait quoi`).
- Sauvegarde/restauration base.
- Mode hors ligne synchronisable.
- Dashboard KPI (CA jour, panier moyen, top ventes).

---

## 9) Proposition de livrables pour ton prof
1. Code source Git.
2. Script SQL d'initialisation.
3. `README.md` (installation + exécution + captures).
4. 1 rapport PDF de ventes.
5. 1 vidéo démo (3-5 min).

---

## 10) Prochaine étape conseillée
Commencer par un **MVP simple en Tkinter + SQLite**, puis ajouter progressivement les modules avancés.

Si tu veux, je peux ensuite te générer :
- la structure de projet prête à lancer ;
- le schéma SQL complet ;
- les écrans Tkinter de base (login, caisse, stock, rapport) ;
- un planning de soutenance avec script de démo.
