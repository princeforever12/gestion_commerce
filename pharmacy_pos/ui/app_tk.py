import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from pharmacy_pos.services.auth_service import User, authenticate, create_user, delete_user, list_users
from pharmacy_pos.services.bootstrap_service import bootstrap
from pharmacy_pos.services.product_service import create_product, delete_product, list_products, search_products
from pharmacy_pos.services.report_service import sales_summary, top_products
from pharmacy_pos.services.sales_service import (
    cancel_sale,
    create_sale,
    get_sale_items,
    list_sales,
    return_sale_item,
)
from pharmacy_pos.services.stock_service import add_stock, get_expiring_batches, get_low_stock_products
from pharmacy_pos.utils.report_export import export_reports_csv
from pharmacy_pos.utils.ticket_export import export_ticket_text


class Palette:
    BG = "#f4f6fb"
    CARD = "#ffffff"
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    TEXT = "#0f172a"
    MUTED = "#64748b"
    SOFT_BLUE = "#e0e7ff"
    SOFT_GRAY = "#f8fafc"


def configure_style(root: tk.Tk) -> None:
    root.configure(bg=Palette.BG)
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("App.TFrame", background=Palette.BG)
    style.configure("Card.TFrame", background=Palette.CARD, relief="flat")

    style.configure("Title.TLabel", background=Palette.BG, foreground=Palette.TEXT, font=("Segoe UI", 18, "bold"))
    style.configure("Subtitle.TLabel", background=Palette.BG, foreground=Palette.MUTED, font=("Segoe UI", 10))
    style.configure("CardTitle.TLabel", background=Palette.CARD, foreground=Palette.TEXT, font=("Segoe UI", 11, "bold"))
    style.configure("Field.TLabel", background=Palette.CARD, foreground=Palette.TEXT, font=("Segoe UI", 10))

    style.configure(
        "Primary.TButton",
        font=("Segoe UI", 10, "bold"),
        foreground="white",
        background=Palette.PRIMARY,
        borderwidth=0,
        padding=(12, 8),
    )
    style.map("Primary.TButton", background=[("active", Palette.PRIMARY_DARK)])

    style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=(10, 7))

    style.configure("TNotebook", background=Palette.BG, borderwidth=0)
    style.configure("TNotebook.Tab", padding=(14, 8), font=("Segoe UI", 10, "bold"))

    style.configure("Treeview", rowheight=28, font=("Segoe UI", 9), background="#ffffff", fieldbackground="#ffffff")
    style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
    style.configure("Status.TLabel", background=Palette.BG, foreground=Palette.MUTED, font=("Segoe UI", 9))


def configure_tree_rows(tree: ttk.Treeview) -> None:
    tree.tag_configure("even", background=Palette.SOFT_GRAY)
    tree.tag_configure("odd", background=Palette.SOFT_BLUE)


def append_tree_row(tree: ttk.Treeview, values: tuple) -> None:
    tag = "even" if len(tree.get_children()) % 2 == 0 else "odd"
    tree.insert("", "end", values=values, tags=(tag,))


class LoginFrame(ttk.Frame):
    def __init__(self, master: tk.Tk, on_login):
        super().__init__(master, padding=24, style="App.TFrame")
        self.on_login = on_login

        wrapper = ttk.Frame(self, style="App.TFrame")
        wrapper.pack(expand=True)

        ttk.Label(wrapper, text="Gestion de caisse Pharmacie", style="Title.TLabel").pack(anchor="center", pady=(10, 4))
        ttk.Label(
            wrapper,
            text="Connectez-vous pour accéder à la caisse, au stock et aux rapports",
            style="Subtitle.TLabel",
        ).pack(anchor="center", pady=(0, 18))

        card = ttk.Frame(wrapper, style="Card.TFrame", padding=20)
        card.pack(fill="x")

        ttk.Label(card, text="Connexion", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        ttk.Label(card, text="Utilisateur", style="Field.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        self.username = ttk.Entry(card, width=36)
        self.username.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(card, text="Mot de passe", style="Field.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        self.password = ttk.Entry(card, show="*", width=36)
        self.password.grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Button(card, text="Se connecter", style="Primary.TButton", command=self._submit).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(14, 0)
        )

        card.columnconfigure(1, weight=1)
        self.username.focus_set()

    def _submit(self) -> None:
        user = authenticate(self.username.get().strip(), self.password.get().strip())
        if user is None:
            messagebox.showerror("Erreur", "Identifiants invalides")
            return
        self.on_login(user)


class DashboardFrame(ttk.Frame):
    def __init__(self, master: tk.Tk, user: User):
        super().__init__(master, padding=16, style="App.TFrame")
        self.user = user

        header = ttk.Frame(self, style="App.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Pharmacie POS", style="Title.TLabel").pack(side="left")
        ttk.Label(
            header,
            text=f"Connecté: {self.user.username} ({self.user.role})",
            style="Subtitle.TLabel",
        ).pack(side="right", pady=(8, 0))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, pady=(12, 0))

        notebook.add(PosTab(notebook, user.id), text="Caisse")
        notebook.add(StockTab(notebook, user.role), text="Stock")
        notebook.add(ReportTab(notebook), text="Rapports")
        notebook.add(SalesHistoryTab(notebook), text="Historique")

        if user.role == "admin":
            notebook.add(UserAdminTab(notebook), text="Utilisateurs")

        ttk.Label(
            self,
            text="Astuce: Double-cliquez/selectionnez les lignes pour accélérer les actions (historique, recherche, stock).",
            style="Status.TLabel",
        ).pack(side="bottom", anchor="w", pady=(8, 0))


class PosTab(ttk.Frame):
    def __init__(self, master, cashier_id: int):
        super().__init__(master, padding=12, style="App.TFrame")
        self.cashier_id = cashier_id

        card = ttk.Frame(self, style="Card.TFrame", padding=14)
        card.pack(fill="both", expand=True)

        ttk.Label(card, text="Vente rapide", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        ttk.Label(card, text="ID produit", style="Field.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Label(card, text="Quantité", style="Field.TLabel").grid(row=1, column=1, sticky="w")
        ttk.Label(card, text="Paiement", style="Field.TLabel").grid(row=1, column=2, sticky="w")
        ttk.Label(card, text="Recherche produit", style="Field.TLabel").grid(row=0, column=4, sticky="w")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)

        self.search_results = ttk.Treeview(card, columns=("id", "name", "barcode", "price", "rx"), show="headings", height=5)
        self.search_results.heading("id", text="ID")
        self.search_results.heading("name", text="Nom")
        self.search_results.heading("barcode", text="Barcode")
        self.search_results.heading("price", text="Prix")
        self.search_results.heading("rx", text="Ord")
        self.search_results.column("id", width=50, anchor="center")
        self.search_results.column("name", width=180, anchor="w")
        self.search_results.column("barcode", width=110, anchor="center")
        self.search_results.column("price", width=80, anchor="e")
        self.search_results.column("rx", width=55, anchor="center")
        self.search_results.bind("<<TreeviewSelect>>", self.on_pick_search_result)
        configure_tree_rows(self.search_results)

        self.product_id_var = tk.StringVar()
        self.quantity_var = tk.StringVar(value="1")
        self.payment_var = tk.StringVar(value="cash")
        self.prescription_ok = tk.BooleanVar(value=False)

        ttk.Entry(card, textvariable=self.product_id_var, width=18).grid(row=2, column=0, padx=(0, 8), pady=(2, 8))
        ttk.Entry(card, textvariable=self.quantity_var, width=18).grid(row=2, column=1, padx=(0, 8), pady=(2, 8))
        ttk.Combobox(card, textvariable=self.payment_var, values=["cash", "carte", "mobile"], width=14, state="readonly").grid(
            row=2, column=2, padx=(0, 8), pady=(2, 8)
        )
        ttk.Checkbutton(card, variable=self.prescription_ok, text="Vérifiée").grid(row=2, column=3, sticky="w")
        ttk.Button(card, text="Ajouter ligne", style="Secondary.TButton", command=self.add_line).grid(row=2, column=4, sticky="w")

        ttk.Entry(card, textvariable=self.search_var, width=30).grid(row=1, column=4, sticky="ew", padx=(8, 0))
        self.search_results.grid(row=2, column=5, rowspan=2, sticky="nsew", padx=(8, 0))

        self.lines = ttk.Treeview(card, columns=("product", "qty", "rx"), show="headings", height=10)
        self.lines.heading("product", text="Produit")
        self.lines.heading("qty", text="Quantité")
        self.lines.heading("rx", text="Ordonnance")
        self.lines.column("product", width=240)
        self.lines.column("qty", width=100, anchor="center")
        self.lines.column("rx", width=120, anchor="center")
        self.lines.grid(row=4, column=0, columnspan=6, sticky="nsew", pady=8)
        configure_tree_rows(self.lines)

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=5, column=0, columnspan=6, sticky="e")
        ttk.Button(actions, text="Vider", style="Secondary.TButton", command=self.clear_lines).pack(side="right", padx=6)
        ttk.Button(actions, text="Valider vente", style="Primary.TButton", command=self.checkout).pack(side="right")

        self.items: list[dict] = []
        card.columnconfigure(4, weight=1)
        card.columnconfigure(5, weight=1)
        card.rowconfigure(4, weight=1)
        self.refresh_search_results()

    def add_line(self) -> None:
        try:
            product_id = int(self.product_id_var.get().strip())
            quantity = int(self.quantity_var.get().strip())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "ID produit et quantité invalides")
            return

        rx_ok = bool(self.prescription_ok.get())
        self.items.append({"product_id": product_id, "quantity": quantity, "prescription_ok": rx_ok})
        append_tree_row(self.lines, (f"Produit #{product_id}", quantity, "Oui" if rx_ok else "Non"))
        self.product_id_var.set("")
        self.quantity_var.set("1")
        self.prescription_ok.set(False)

    def on_search_change(self, *_args) -> None:
        self.refresh_search_results()

    def refresh_search_results(self) -> None:
        for iid in self.search_results.get_children():
            self.search_results.delete(iid)
        for row in search_products(self.search_var.get(), 20):
            append_tree_row(
                self.search_results,
                (
                    row["id"],
                    row["name"],
                    row["barcode"] or "",
                    f"{row['sell_price']:.2f}",
                    "Oui" if row["requires_prescription"] else "Non",
                ),
            )

    def on_pick_search_result(self, _event=None) -> None:
        selected = self.search_results.selection()
        if not selected:
            return
        values = self.search_results.item(selected[0], "values")
        if not values:
            return
        self.product_id_var.set(str(values[0]))

    def clear_lines(self) -> None:
        self.items.clear()
        for iid in self.lines.get_children():
            self.lines.delete(iid)

    def checkout(self) -> None:
        try:
            sale_id = create_sale(self.cashier_id, self.items, self.payment_var.get().strip())
        except Exception as exc:
            messagebox.showerror("Vente impossible", str(exc))
            return

        messagebox.showinfo("Succès", f"Vente enregistrée ID={sale_id}")
        self.clear_lines()


class StockTab(ttk.Frame):
    def __init__(self, master, role: str):
        super().__init__(master, padding=12, style="App.TFrame")
        self.role = role
        self.can_manage = role == "admin"

        container = ttk.Frame(self, style="App.TFrame")
        container.pack(fill="both", expand=True)

        left = ttk.Frame(container, style="Card.TFrame", padding=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        right_wrap = ttk.Frame(container, style="Card.TFrame")
        right_wrap.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        right_canvas = tk.Canvas(
            right_wrap,
            background=Palette.CARD,
            borderwidth=0,
            highlightthickness=0,
        )
        right_scroll = ttk.Scrollbar(right_wrap, orient="vertical", command=right_canvas.yview)
        right_canvas.configure(yscrollcommand=right_scroll.set)

        right_scroll.pack(side="right", fill="y")
        right_canvas.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(right_canvas, style="Card.TFrame", padding=12)
        right_window = right_canvas.create_window((0, 0), window=right, anchor="nw")

        def _sync_right_scroll(_event=None) -> None:
            right_canvas.configure(scrollregion=right_canvas.bbox("all"))
            right_canvas.itemconfigure(right_window, width=right_canvas.winfo_width())

        right.bind("<Configure>", _sync_right_scroll)
        right_canvas.bind("<Configure>", _sync_right_scroll)

        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=1)

        top_controls = ttk.Frame(left, style="Card.TFrame")
        top_controls.pack(fill="x", pady=(0, 8))
        ttk.Label(top_controls, text="Produits en stock", style="CardTitle.TLabel").pack(side="left")
        ttk.Button(top_controls, text="Supprimer produit", style="Secondary.TButton", command=self.delete_selected_product).pack(side="right", padx=(0, 6))
        ttk.Button(top_controls, text="Rafraîchir", style="Secondary.TButton", command=self.refresh_products).pack(side="right", padx=(0, 6))

        self.products = ttk.Treeview(left, columns=("id", "name", "stock", "sell", "min"), show="headings", height=16)
        for col, txt, w in [
            ("id", "ID", 60),
            ("name", "Nom", 180),
            ("stock", "Stock", 80),
            ("sell", "Prix vente", 90),
            ("min", "Min", 70),
        ]:
            self.products.heading(col, text=txt)
            self.products.column(col, width=w, anchor="center" if col != "name" else "w")
        self.products.pack(fill="both", expand=True, pady=(0, 8))
        configure_tree_rows(self.products)

        actions_left = ttk.Frame(left, style="Card.TFrame")
        actions_left.pack(anchor="e")
        ttk.Button(actions_left, text="Alertes stock bas", style="Primary.TButton", command=self.show_alerts).pack(side="left", padx=(0, 6))
        ttk.Button(actions_left, text="Péremptions <= 90j", style="Secondary.TButton", command=self.show_expiry_alerts).pack(side="left")

        ttk.Label(right, text="Nouveau produit", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")

        self.p_name = tk.StringVar()
        self.p_cat = tk.StringVar(value="Divers")
        self.p_buy = tk.StringVar(value="0")
        self.p_sell = tk.StringVar(value="0")
        self.p_tva = tk.StringVar(value="0")
        self.p_min = tk.StringVar(value="0")
        self.p_rx = tk.BooleanVar(value=False)

        fields = [
            ("Nom", self.p_name),
            ("Catégorie", self.p_cat),
            ("Prix achat", self.p_buy),
            ("Prix vente", self.p_sell),
            ("TVA", self.p_tva),
            ("Stock min", self.p_min),
        ]
        for idx, (label, var) in enumerate(fields, start=1):
            ttk.Label(right, text=label, style="Field.TLabel").grid(row=idx, column=0, sticky="w", pady=2)
            entry = ttk.Entry(right, textvariable=var, width=20)
            entry.grid(row=idx, column=1, sticky="ew", pady=2)
            if not self.can_manage:
                entry.state(["disabled"])

        rx_chk = ttk.Checkbutton(right, text="Ordonnance requise", variable=self.p_rx)
        rx_chk.grid(row=7, column=0, columnspan=2, sticky="w", pady=(6, 2))

        ttk.Label(
            right,
            text="Barcode généré automatiquement",
            style="Subtitle.TLabel",
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=(0, 4))

        create_btn = ttk.Button(right, text="Créer produit", style="Primary.TButton", command=self.create_product_ui)
        create_btn.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(6, 12))

        ttk.Separator(right, orient="horizontal").grid(row=10, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Label(right, text="Ajouter lot", style="CardTitle.TLabel").grid(row=11, column=0, columnspan=2, sticky="w")

        self.s_pid = tk.StringVar()
        self.s_batch = tk.StringVar()
        self.s_exp = tk.StringVar(value="2027-12-31")
        self.s_qty = tk.StringVar(value="1")

        stock_fields = [
            ("ID produit", self.s_pid),
            ("N° lot", self.s_batch),
            ("Expiration", self.s_exp),
            ("Quantité", self.s_qty),
        ]
        for idx, (label, var) in enumerate(stock_fields, start=12):
            ttk.Label(right, text=label, style="Field.TLabel").grid(row=idx, column=0, sticky="w", pady=2)
            entry = ttk.Entry(right, textvariable=var, width=20)
            entry.grid(row=idx, column=1, sticky="ew", pady=2)
            if not self.can_manage:
                entry.state(["disabled"])

        add_btn = ttk.Button(right, text="Ajouter stock", style="Secondary.TButton", command=self.add_stock_ui)
        add_btn.grid(row=16, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        if not self.can_manage:
            create_btn.state(["disabled"])
            add_btn.state(["disabled"])
            rx_chk.state(["disabled"])
            ttk.Label(
                right,
                text="Mode lecture seule pour ce rôle (admin requis).",
                style="Subtitle.TLabel",
            ).grid(row=17, column=0, columnspan=2, sticky="w", pady=(8, 0))

        right.columnconfigure(1, weight=1)
        self.refresh_products()

    def refresh_products(self) -> None:
        for iid in self.products.get_children():
            self.products.delete(iid)

        for p in list_products():
            append_tree_row(
                self.products,
                (p["id"], p["name"], p["stock"], f"{p['sell_price']:.2f}", p["min_stock"]),
            )

    def create_product_ui(self) -> None:
        if not self.can_manage:
            messagebox.showwarning("Accès refusé", "Seul un admin peut créer des produits")
            return
        try:
            pid = create_product(
                name=self.p_name.get().strip(),
                barcode=None,
                category_name=self.p_cat.get().strip(),
                buy_price=float(self.p_buy.get().strip()),
                sell_price=float(self.p_sell.get().strip()),
                tva=float(self.p_tva.get().strip()),
                min_stock=int(self.p_min.get().strip()),
                requires_prescription=bool(self.p_rx.get()),
            )
        except Exception as exc:
            messagebox.showerror("Erreur produit", str(exc))
            return

        messagebox.showinfo("Succès", f"Produit créé ID={pid}")
        self.refresh_products()

    def add_stock_ui(self) -> None:
        if not self.can_manage:
            messagebox.showwarning("Accès refusé", "Seul un admin peut ajouter du stock")
            return
        try:
            batch_id = add_stock(
                product_id=int(self.s_pid.get().strip()),
                batch_number=self.s_batch.get().strip(),
                expiry_date=self.s_exp.get().strip(),
                quantity=int(self.s_qty.get().strip()),
            )
        except Exception as exc:
            messagebox.showerror("Erreur stock", str(exc))
            return

        messagebox.showinfo("Succès", f"Lot ajouté ID={batch_id}")
        self.refresh_products()



    def delete_selected_product(self) -> None:
        if not self.can_manage:
            messagebox.showwarning("Accès refusé", "Seul un admin peut supprimer un produit")
            return

        selected = self.products.selection()
        if not selected:
            messagebox.showwarning("Suppression", "Sélectionnez un produit à supprimer")
            return

        values = self.products.item(selected[0], "values")
        product_id = int(values[0])
        product_name = str(values[1])

        confirm = messagebox.askyesno(
            "Confirmer suppression",
            f"Supprimer le produit '{product_name}' (ID={product_id}) ?",
        )
        if not confirm:
            return

        try:
            delete_product(product_id)
        except Exception as exc:
            messagebox.showerror("Erreur suppression", str(exc))
            return

        messagebox.showinfo("Succès", "Produit supprimé")
        self.refresh_products()

    def show_expiry_alerts(self) -> None:
        rows = get_expiring_batches(90)
        if not rows:
            messagebox.showinfo("Péremption", "Aucun lot à risque dans les 90 jours")
            return

        lines = [
            f"- {r['product_name']} | lot={r['batch_number']} | exp={r['expiry_date']} | qte={r['quantity']}"
            for r in rows[:20]
        ]
        if len(rows) > 20:
            lines.append(f"... et {len(rows)-20} autre(s)")
        messagebox.showwarning("Lots à péremption proche", "\n".join(lines))

    def show_alerts(self) -> None:
        alerts = get_low_stock_products()
        if not alerts:
            messagebox.showinfo("Alertes", "Aucune alerte de stock bas")
            return

        message = "\n".join([f"- {a['name']}: {a['stock']} (min={a['min_stock']})" for a in alerts])
        messagebox.showwarning("Stock bas", message)


class SalesHistoryTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12, style="App.TFrame")

        card = ttk.Frame(self, style="Card.TFrame", padding=12)
        card.pack(fill="both", expand=True)

        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text="Historique des ventes", style="CardTitle.TLabel").pack(side="left")
        ttk.Button(top, text="Retour ligne", style="Secondary.TButton", command=self.return_selected_item).pack(side="right", padx=(0, 6))
        ttk.Button(top, text="Annuler ticket", style="Secondary.TButton", command=self.cancel_selected_sale).pack(side="right", padx=(0, 6))
        ttk.Button(top, text="Exporter ticket", style="Secondary.TButton", command=self.export_selected_ticket).pack(side="right", padx=(0, 6))
        ttk.Button(top, text="Rafraîchir", style="Secondary.TButton", command=self.refresh).pack(side="right")

        self.sales = ttk.Treeview(card, columns=("id", "cashier", "total", "payment", "date", "status"), show="headings", height=10)
        for col, title, width in [
            ("id", "ID", 70),
            ("cashier", "Caissier", 140),
            ("total", "Total TTC", 100),
            ("payment", "Paiement", 110),
            ("date", "Date", 180),
            ("status", "Statut", 100),
        ]:
            self.sales.heading(col, text=title)
            self.sales.column(col, width=width, anchor="center" if col != "cashier" else "w")
        self.sales.pack(fill="x", pady=(8, 10))
        self.sales.bind("<<TreeviewSelect>>", self.on_select_sale)
        configure_tree_rows(self.sales)

        ttk.Label(card, text="Détail de la vente sélectionnée", style="CardTitle.TLabel").pack(anchor="w", pady=(4, 6))
        self.items = ttk.Treeview(card, columns=("product", "qty", "unit", "line", "batch", "sid"), show="headings", height=9)
        self.items.heading("product", text="Produit")
        self.items.heading("qty", text="Qté")
        self.items.heading("unit", text="Prix U.")
        self.items.heading("line", text="Total ligne")
        self.items.heading("batch", text="Lot")
        self.items.heading("sid", text="sale_item_id")
        self.items.column("product", width=220, anchor="w")
        self.items.column("qty", width=70, anchor="center")
        self.items.column("unit", width=90, anchor="e")
        self.items.column("line", width=110, anchor="e")
        self.items.column("batch", width=120, anchor="center")
        self.items.column("sid", width=0, stretch=False)
        self.items.pack(fill="both", expand=True)
        configure_tree_rows(self.items)

        self.refresh()

    def export_csv_reports(self) -> None:
        directory = filedialog.askdirectory(title="Choisir dossier d'export CSV")
        if not directory:
            return

        try:
            files = export_reports_csv(directory)
        except Exception as exc:
            messagebox.showerror("Export CSV", str(exc))
            return

        messagebox.showinfo("Export CSV", "Fichiers générés:\n- " + "\n- ".join(files))

    def refresh(self) -> None:
        for iid in self.sales.get_children():
            self.sales.delete(iid)
        for row in list_sales(200):
            append_tree_row(
                self.sales,
                (row["id"], row["cashier"], f"{row['total_ttc']:.2f}", row["payment_method"], row["created_at"], "Annulée" if row["canceled"] else "Active"),
            )

        for iid in self.items.get_children():
            self.items.delete(iid)

    def export_selected_ticket(self) -> None:
        selected = self.sales.selection()
        if not selected:
            messagebox.showwarning("Export", "Sélectionne une vente d'abord")
            return

        values = self.sales.item(selected[0], "values")
        sale_id = int(values[0])

        filename = filedialog.asksaveasfilename(
            title="Exporter ticket",
            defaultextension=".txt",
            filetypes=[("Fichier texte", "*.txt")],
            initialfile=f"ticket_{sale_id}.txt",
        )
        if not filename:
            return

        path = export_ticket_text(sale_id, filename)
        messagebox.showinfo("Export", f"Ticket exporté: {path}")

    def cancel_selected_sale(self) -> None:
        selected = self.sales.selection()
        if not selected:
            messagebox.showwarning("Annulation", "Sélectionne une vente")
            return

        values = self.sales.item(selected[0], "values")
        sale_id = int(values[0])
        if len(values) >= 6 and values[5] == "Annulée":
            messagebox.showinfo("Annulation", "Cette vente est déjà annulée")
            return

        reason = simpledialog.askstring("Annulation ticket", "Motif d'annulation:", initialvalue="Erreur caisse")
        if reason is None:
            return

        try:
            cancel_sale(sale_id, reason)
        except Exception as exc:
            messagebox.showerror("Annulation impossible", str(exc))
            return

        messagebox.showinfo("Succès", f"Vente #{sale_id} annulée")
        self.refresh()

    def return_selected_item(self) -> None:
        selected_sale = self.sales.selection()
        selected_item = self.items.selection()
        if not selected_sale or not selected_item:
            messagebox.showwarning("Retour", "Sélectionne une vente puis une ligne de ticket")
            return

        sale_values = self.sales.item(selected_sale[0], "values")
        if len(sale_values) >= 6 and sale_values[5] == "Annulée":
            messagebox.showwarning("Retour", "Retour impossible: ticket annulé")
            return

        item_values = self.items.item(selected_item[0], "values")
        sale_item_id = int(item_values[5])
        qty_max = int(item_values[1])
        qty = simpledialog.askinteger("Retour", f"Quantité à retourner (max {qty_max})", minvalue=1, maxvalue=qty_max)
        if qty is None:
            return

        reason = simpledialog.askstring("Retour", "Motif du retour:", initialvalue="Retour client")
        if reason is None:
            return

        try:
            return_sale_item(sale_item_id, qty, reason)
        except Exception as exc:
            messagebox.showerror("Retour impossible", str(exc))
            return

        messagebox.showinfo("Succès", f"Retour enregistré pour la ligne #{sale_item_id}")
        self.on_select_sale()
        self.refresh()

    def on_select_sale(self, _event=None) -> None:
        selected = self.sales.selection()
        if not selected:
            return
        values = self.sales.item(selected[0], "values")
        if not values:
            return

        sale_id = int(values[0])
        rows = get_sale_items(sale_id)

        for iid in self.items.get_children():
            self.items.delete(iid)

        for row in rows:
            append_tree_row(
                self.items,
                (
                    row["product_name"],
                    row["quantity"],
                    f"{row['unit_price']:.2f}",
                    f"{row['line_total']:.2f}",
                    row["batch_number"],
                    row["sale_item_id"],
                ),
            )


class UserAdminTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12, style="App.TFrame")

        card = ttk.Frame(self, style="Card.TFrame", padding=12)
        card.pack(fill="both", expand=True)

        ttk.Label(card, text="Gestion des utilisateurs", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")

        self.u_name = tk.StringVar()
        self.u_pass = tk.StringVar()
        self.u_role = tk.StringVar(value="caissier")

        ttk.Label(card, text="Nom utilisateur", style="Field.TLabel").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(card, textvariable=self.u_name).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(card, text="Mot de passe", style="Field.TLabel").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(card, textvariable=self.u_pass, show="*").grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(card, text="Rôle", style="Field.TLabel").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Combobox(card, textvariable=self.u_role, values=["admin", "caissier", "pharmacien"], state="readonly").grid(
            row=3, column=1, sticky="ew", pady=2
        )

        ttk.Button(card, text="Créer utilisateur", style="Primary.TButton", command=self.create_user_ui).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(8, 10)
        )

        self.users = ttk.Treeview(card, columns=("id", "username", "role", "created"), show="headings", height=12)
        self.users.heading("id", text="ID")
        self.users.heading("username", text="Utilisateur")
        self.users.heading("role", text="Rôle")
        self.users.heading("created", text="Créé le")
        self.users.column("id", width=60, anchor="center")
        self.users.column("username", width=180, anchor="w")
        self.users.column("role", width=100, anchor="center")
        self.users.column("created", width=180, anchor="center")
        self.users.grid(row=5, column=0, columnspan=2, sticky="nsew")
        configure_tree_rows(self.users)

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=6, column=0, columnspan=2, sticky="e", pady=(8, 0))
        ttk.Button(actions, text="Supprimer utilisateur", style="Secondary.TButton", command=self.delete_selected_user).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Rafraîchir", style="Secondary.TButton", command=self.refresh_users).pack(side="left")

        card.columnconfigure(1, weight=1)
        card.rowconfigure(5, weight=1)
        self.refresh_users()

    def create_user_ui(self) -> None:
        try:
            uid = create_user(self.u_name.get(), self.u_pass.get(), self.u_role.get())
        except Exception as exc:
            messagebox.showerror("Erreur utilisateur", str(exc))
            return

        messagebox.showinfo("Succès", f"Utilisateur créé ID={uid}")
        self.u_name.set("")
        self.u_pass.set("")
        self.u_role.set("caissier")
        self.refresh_users()

    def delete_selected_user(self) -> None:
        selected = self.users.selection()
        if not selected:
            messagebox.showwarning("Suppression", "Sélectionnez un utilisateur à supprimer")
            return

        values = self.users.item(selected[0], "values")
        user_id = int(values[0])
        username = str(values[1])

        confirm = messagebox.askyesno(
            "Confirmer suppression",
            f"Supprimer l'utilisateur '{username}' (ID={user_id}) ?",
        )
        if not confirm:
            return

        try:
            delete_user(user_id)
        except Exception as exc:
            messagebox.showerror("Erreur suppression", str(exc))
            return

        messagebox.showinfo("Succès", "Utilisateur supprimé")
        self.refresh_users()

    def refresh_users(self) -> None:
        for iid in self.users.get_children():
            self.users.delete(iid)

        for user in list_users():
            append_tree_row(
                self.users,
                (user["id"], user["username"], user["role"], user["created_at"]),
            )


class ReportTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12, style="App.TFrame")

        card = ttk.Frame(self, style="Card.TFrame", padding=12)
        card.pack(fill="both", expand=True)

        top_bar = ttk.Frame(card, style="Card.TFrame")
        top_bar.pack(fill="x")
        ttk.Label(top_bar, text="Rapports", style="CardTitle.TLabel").pack(side="left")

        ttk.Label(top_bar, text="Période", style="Subtitle.TLabel").pack(side="left", padx=(16, 6))
        self.period_var = tk.StringVar(value="jour")
        self.period_select = ttk.Combobox(
            top_bar,
            textvariable=self.period_var,
            values=("jour", "semaine", "mois", "annee"),
            state="readonly",
            width=10,
        )
        self.period_select.pack(side="left")
        self.period_select.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

        ttk.Button(top_bar, text="Exporter CSV", style="Secondary.TButton", command=self.export_csv_reports).pack(side="right", padx=(0, 6))
        ttk.Button(top_bar, text="Rafraîchir", style="Primary.TButton", command=self.refresh).pack(side="right")

        metrics = ttk.Frame(card, style="Card.TFrame")
        metrics.pack(fill="x", pady=(10, 8))

        self.nb_ventes = tk.StringVar(value="0")
        self.total_ht = tk.StringVar(value="0.00")
        self.total_tva = tk.StringVar(value="0.00")
        self.total_ttc = tk.StringVar(value="0.00")

        for idx, (label, var) in enumerate(
            [
                ("Nombre ventes", self.nb_ventes),
                ("Total HT", self.total_ht),
                ("Total TVA", self.total_tva),
                ("Total TTC", self.total_ttc),
            ]
        ):
            box = ttk.Frame(metrics, style="Card.TFrame", padding=10)
            box.grid(row=0, column=idx, padx=6, sticky="nsew")
            ttk.Label(box, text=label, style="Subtitle.TLabel").pack(anchor="w")
            ttk.Label(box, textvariable=var, style="CardTitle.TLabel").pack(anchor="w", pady=(4, 0))
            metrics.columnconfigure(idx, weight=1)

        ttk.Label(card, text="Top produits", style="CardTitle.TLabel").pack(anchor="w", pady=(12, 6))
        self.top = ttk.Treeview(card, columns=("name", "qty", "amount"), show="headings", height=10)
        self.top.heading("name", text="Produit")
        self.top.heading("qty", text="Qté")
        self.top.heading("amount", text="Montant")
        self.top.column("name", width=220, anchor="w")
        self.top.column("qty", width=90, anchor="center")
        self.top.column("amount", width=130, anchor="e")
        self.top.pack(fill="both", expand=True)
        configure_tree_rows(self.top)

        self.refresh()

    def export_csv_reports(self) -> None:
        directory = filedialog.askdirectory(title="Choisir dossier d'export CSV")
        if not directory:
            return

        try:
            files = export_reports_csv(directory)
        except Exception as exc:
            messagebox.showerror("Export CSV", str(exc))
            return

        messagebox.showinfo("Export CSV", "Fichiers générés:\n- " + "\n- ".join(files))

    def refresh(self) -> None:
        period = self.period_var.get().strip() or "jour"
        data = sales_summary(period)
        self.nb_ventes.set(str(data["nb_ventes"]))
        self.total_ht.set(f"{data['total_ht']:.2f}")
        self.total_tva.set(f"{data['total_tva']:.2f}")
        self.total_ttc.set(f"{data['total_ttc']:.2f}")

        for iid in self.top.get_children():
            self.top.delete(iid)
        for row in top_products(period=period):
            append_tree_row(self.top, (row["name"], row["qty_vendue"], f"{row['montant']:.2f}"))


class PharmacyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pharmacie POS - MVP")
        self.geometry("1000x700")
        self.minsize(920, 620)

        configure_style(self)
        bootstrap()
        self.current = None
        self.show_login()

    def show_login(self) -> None:
        self._swap(LoginFrame(self, self.on_login))

    def on_login(self, user: User) -> None:
        self._swap(DashboardFrame(self, user))

    def _swap(self, frame: ttk.Frame) -> None:
        if self.current is not None:
            self.current.destroy()
        self.current = frame
        self.current.pack(fill="both", expand=True)


def run() -> None:
    app = PharmacyApp()
    app.mainloop()
