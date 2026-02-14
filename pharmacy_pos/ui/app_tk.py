import tkinter as tk
from tkinter import messagebox, ttk

from pharmacy_pos.services.auth_service import User, authenticate
from pharmacy_pos.services.bootstrap_service import bootstrap
from pharmacy_pos.services.product_service import create_product, list_products
from pharmacy_pos.services.report_service import daily_sales_summary, top_products
from pharmacy_pos.services.sales_service import create_sale
from pharmacy_pos.services.stock_service import add_stock, get_low_stock_products


 codex/propose-complete-cash-register-system-design-ah3cit
class Palette:
    BG = "#f4f6fb"
    CARD = "#ffffff"
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    TEXT = "#0f172a"
    MUTED = "#64748b"


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

    style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
    style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))


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
class LoginFrame(ttk.Frame):
    def __init__(self, master: tk.Tk, on_login):
        super().__init__(master, padding=16)
        self.on_login = on_login

        ttk.Label(self, text="Gestion de caisse Pharmacie", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 16)
        )

        ttk.Label(self, text="Utilisateur").grid(row=1, column=0, sticky="w")
        self.username = ttk.Entry(self)
        self.username.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(self, text="Mot de passe").grid(row=2, column=0, sticky="w")
        self.password = ttk.Entry(self, show="*")
        self.password.grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Button(self, text="Se connecter", command=self._submit).grid(
            row=3, column=0, columnspan=2, pady=12
        )

        self.columnconfigure(1, weight=1)
 main

    def _submit(self) -> None:
        user = authenticate(self.username.get().strip(), self.password.get().strip())
        if user is None:
            messagebox.showerror("Erreur", "Identifiants invalides")
            return
        self.on_login(user)


class DashboardFrame(ttk.Frame):
    def __init__(self, master: tk.Tk, user: User):
 codex/propose-complete-cash-register-system-design-ah3cit
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
        notebook.add(StockTab(notebook), text="Stock")
        notebook.add(ReportTab(notebook), text="Rapports")

        super().__init__(master, padding=12)
        self.user = user

        header = ttk.Frame(self)
        header.pack(fill="x")
        ttk.Label(
            header,
            text=f"Connecté: {self.user.username} ({self.user.role})",
            font=("Arial", 11, "bold"),
        ).pack(side="left")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, pady=(10, 0))

        self.pos_tab = PosTab(notebook, user.id)
        self.stock_tab = StockTab(notebook)
        self.report_tab = ReportTab(notebook)

        notebook.add(self.pos_tab, text="Caisse")
        notebook.add(self.stock_tab, text="Stock")
        notebook.add(self.report_tab, text="Rapports")
 main


class PosTab(ttk.Frame):
    def __init__(self, master, cashier_id: int):
 codex/propose-complete-cash-register-system-design-ah3cit
        super().__init__(master, padding=12, style="App.TFrame")
        self.cashier_id = cashier_id

        card = ttk.Frame(self, style="Card.TFrame", padding=14)
        card.pack(fill="both", expand=True)

        ttk.Label(card, text="Vente rapide", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        ttk.Label(card, text="ID produit", style="Field.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Label(card, text="Quantité", style="Field.TLabel").grid(row=1, column=1, sticky="w")
        ttk.Label(card, text="Paiement", style="Field.TLabel").grid(row=1, column=2, sticky="w")

        self.product_id_var = tk.StringVar()
        self.quantity_var = tk.StringVar(value="1")
        self.payment_var = tk.StringVar(value="cash")

        ttk.Entry(card, textvariable=self.product_id_var, width=18).grid(row=2, column=0, padx=(0, 8), pady=(2, 8))
        ttk.Entry(card, textvariable=self.quantity_var, width=18).grid(row=2, column=1, padx=(0, 8), pady=(2, 8))
        ttk.Combobox(card, textvariable=self.payment_var, values=["cash", "carte", "mobile"], width=14, state="readonly").grid(
            row=2, column=2, padx=(0, 8), pady=(2, 8)
        )
        ttk.Button(card, text="Ajouter ligne", style="Secondary.TButton", command=self.add_line).grid(row=2, column=3, sticky="w")

        self.lines = ttk.Treeview(card, columns=("product", "qty"), show="headings", height=10)
        self.lines.heading("product", text="Produit")
        self.lines.heading("qty", text="Quantité")
        self.lines.column("product", width=240)
        self.lines.column("qty", width=100, anchor="center")
        self.lines.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=8)

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=4, column=0, columnspan=4, sticky="e")
        ttk.Button(actions, text="Vider", style="Secondary.TButton", command=self.clear_lines).pack(side="right", padx=6)
        ttk.Button(actions, text="Valider vente", style="Primary.TButton", command=self.checkout).pack(side="right")

        self.items: list[dict] = []
        card.columnconfigure(0, weight=1)
        card.rowconfigure(3, weight=1)

        super().__init__(master, padding=8)
        self.cashier_id = cashier_id

        ttk.Label(self, text="Vente rapide", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )

        ttk.Label(self, text="ID produit").grid(row=1, column=0, sticky="w")
        ttk.Label(self, text="Quantité").grid(row=1, column=1, sticky="w")

        self.product_id_var = tk.StringVar()
        self.quantity_var = tk.StringVar(value="1")

        ttk.Entry(self, textvariable=self.product_id_var, width=16).grid(row=2, column=0, padx=(0, 8))
        ttk.Entry(self, textvariable=self.quantity_var, width=16).grid(row=2, column=1, padx=(0, 8))
        ttk.Button(self, text="Ajouter ligne", command=self.add_line).grid(row=2, column=2, sticky="w")

        self.lines = tk.Listbox(self, height=7)
        self.lines.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=8)

        pay_row = ttk.Frame(self)
        pay_row.grid(row=4, column=0, columnspan=3, sticky="ew")
        ttk.Label(pay_row, text="Paiement").pack(side="left")
        self.payment_var = tk.StringVar(value="cash")
        ttk.Combobox(pay_row, textvariable=self.payment_var, values=["cash", "carte", "mobile"], width=12).pack(
            side="left", padx=8
        )
        ttk.Button(pay_row, text="Valider vente", command=self.checkout).pack(side="left")

        self.items: list[dict] = []
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
 main

    def add_line(self) -> None:
        try:
            product_id = int(self.product_id_var.get().strip())
            quantity = int(self.quantity_var.get().strip())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "ID produit et quantité invalides")
            return

        self.items.append({"product_id": product_id, "quantity": quantity})
 codex/propose-complete-cash-register-system-design-ah3cit
        self.lines.insert("", "end", values=(f"Produit #{product_id}", quantity))
        self.product_id_var.set("")
        self.quantity_var.set("1")

    def clear_lines(self) -> None:
        self.items.clear()
        for iid in self.lines.get_children():
            self.lines.delete(iid)


        self.lines.insert("end", f"Produit #{product_id} x{quantity}")
        self.product_id_var.set("")
        self.quantity_var.set("1")

 main
    def checkout(self) -> None:
        try:
            sale_id = create_sale(self.cashier_id, self.items, self.payment_var.get().strip())
        except Exception as exc:
            messagebox.showerror("Vente impossible", str(exc))
            return

        messagebox.showinfo("Succès", f"Vente enregistrée ID={sale_id}")
 codex/propose-complete-cash-register-system-design-ah3cit
        self.clear_lines()

        self.items.clear()
        self.lines.delete(0, "end")
 main


class StockTab(ttk.Frame):
    def __init__(self, master):
 codex/propose-complete-cash-register-system-design-ah3cit
        super().__init__(master, padding=12, style="App.TFrame")

        container = ttk.Frame(self, style="App.TFrame")
        container.pack(fill="both", expand=True)

        left = ttk.Frame(container, style="Card.TFrame", padding=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = ttk.Frame(container, style="Card.TFrame", padding=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=1)

        ttk.Label(left, text="Produits en stock", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Button(left, text="Rafraîchir", style="Secondary.TButton", command=self.refresh_products).pack(anchor="e", pady=(0, 8))

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

        ttk.Button(left, text="Voir alertes stock bas", style="Primary.TButton", command=self.show_alerts).pack(anchor="e")

        ttk.Label(right, text="Nouveau produit", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")

        super().__init__(master, padding=8)

        ttk.Label(self, text="Produits", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Button(self, text="Rafraîchir", command=self.refresh_products).grid(row=0, column=1, sticky="e")

        self.products = tk.Listbox(self, height=8)
        self.products.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(6, 12))

        add_product = ttk.LabelFrame(self, text="Nouveau produit")
        add_product.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
 main

        self.p_name = tk.StringVar()
        self.p_barcode = tk.StringVar()
        self.p_cat = tk.StringVar(value="Divers")
        self.p_buy = tk.StringVar(value="0")
        self.p_sell = tk.StringVar(value="0")
        self.p_tva = tk.StringVar(value="0")
        self.p_min = tk.StringVar(value="0")

        fields = [
            ("Nom", self.p_name),
            ("Barcode", self.p_barcode),
            ("Catégorie", self.p_cat),
            ("Prix achat", self.p_buy),
            ("Prix vente", self.p_sell),
            ("TVA", self.p_tva),
            ("Stock min", self.p_min),
        ]
 codex/propose-complete-cash-register-system-design-ah3cit
        for idx, (label, var) in enumerate(fields, start=1):
            ttk.Label(right, text=label, style="Field.TLabel").grid(row=idx, column=0, sticky="w", pady=2)
            ttk.Entry(right, textvariable=var, width=20).grid(row=idx, column=1, sticky="ew", pady=2)

        ttk.Button(right, text="Créer produit", style="Primary.TButton", command=self.create_product_ui).grid(
            row=8, column=0, columnspan=2, sticky="ew", pady=(8, 12)
        )

        ttk.Separator(right, orient="horizontal").grid(row=9, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Label(right, text="Ajouter lot", style="CardTitle.TLabel").grid(row=10, column=0, columnspan=2, sticky="w")


        for idx, (label, var) in enumerate(fields):
            ttk.Label(add_product, text=label).grid(row=idx, column=0, sticky="w", padx=6, pady=2)
            ttk.Entry(add_product, textvariable=var, width=22).grid(row=idx, column=1, sticky="ew", padx=6, pady=2)

        ttk.Button(add_product, text="Créer produit", command=self.create_product_ui).grid(
            row=len(fields), column=0, columnspan=2, pady=8
        )
        add_product.columnconfigure(1, weight=1)

        add_stock_box = ttk.LabelFrame(self, text="Ajouter lot")
        add_stock_box.grid(row=3, column=0, columnspan=2, sticky="ew")
 main
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
 codex/propose-complete-cash-register-system-design-ah3cit
        for idx, (label, var) in enumerate(stock_fields, start=11):
            ttk.Label(right, text=label, style="Field.TLabel").grid(row=idx, column=0, sticky="w", pady=2)
            ttk.Entry(right, textvariable=var, width=20).grid(row=idx, column=1, sticky="ew", pady=2)

        ttk.Button(right, text="Ajouter stock", style="Secondary.TButton", command=self.add_stock_ui).grid(
            row=15, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )

        right.columnconfigure(1, weight=1)
        self.refresh_products()

    def refresh_products(self) -> None:
        for iid in self.products.get_children():
            self.products.delete(iid)

        for p in list_products():
            self.products.insert(
                "",
                "end",
                values=(p["id"], p["name"], p["stock"], f"{p['sell_price']:.2f}", p["min_stock"]),

        for idx, (label, var) in enumerate(stock_fields):
            ttk.Label(add_stock_box, text=label).grid(row=idx, column=0, sticky="w", padx=6, pady=2)
            ttk.Entry(add_stock_box, textvariable=var, width=22).grid(row=idx, column=1, sticky="ew", padx=6, pady=2)

        ttk.Button(add_stock_box, text="Ajouter stock", command=self.add_stock_ui).grid(
            row=len(stock_fields), column=0, columnspan=2, pady=8
        )
        add_stock_box.columnconfigure(1, weight=1)

        ttk.Button(self, text="Voir alertes stock bas", command=self.show_alerts).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.refresh_products()

    def refresh_products(self) -> None:
        self.products.delete(0, "end")
        for p in list_products():
            self.products.insert(
                "end",
                f"#{p['id']} {p['name']} | stock={p['stock']} | vente={p['sell_price']} | min={p['min_stock']}",
 main
            )

    def create_product_ui(self) -> None:
        try:
            pid = create_product(
                name=self.p_name.get().strip(),
                barcode=self.p_barcode.get().strip(),
                category_name=self.p_cat.get().strip(),
                buy_price=float(self.p_buy.get().strip()),
                sell_price=float(self.p_sell.get().strip()),
                tva=float(self.p_tva.get().strip()),
                min_stock=int(self.p_min.get().strip()),
                requires_prescription=False,
            )
        except Exception as exc:
            messagebox.showerror("Erreur produit", str(exc))
            return

        messagebox.showinfo("Succès", f"Produit créé ID={pid}")
        self.refresh_products()

    def add_stock_ui(self) -> None:
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

    def show_alerts(self) -> None:
        alerts = get_low_stock_products()
        if not alerts:
            messagebox.showinfo("Alertes", "Aucune alerte de stock bas")
            return

        message = "\n".join([f"- {a['name']}: {a['stock']} (min={a['min_stock']})" for a in alerts])
        messagebox.showwarning("Stock bas", message)


class ReportTab(ttk.Frame):
    def __init__(self, master):
 codex/propose-complete-cash-register-system-design-ah3cit
        super().__init__(master, padding=12, style="App.TFrame")

        card = ttk.Frame(self, style="Card.TFrame", padding=12)
        card.pack(fill="both", expand=True)

        top_bar = ttk.Frame(card, style="Card.TFrame")
        top_bar.pack(fill="x")
        ttk.Label(top_bar, text="Rapports du jour", style="CardTitle.TLabel").pack(side="left")
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

        self.refresh()

    def refresh(self) -> None:
        data = daily_sales_summary()
        self.nb_ventes.set(str(data["nb_ventes"]))
        self.total_ht.set(f"{data['total_ht']:.2f}")
        self.total_tva.set(f"{data['total_tva']:.2f}")
        self.total_ttc.set(f"{data['total_ttc']:.2f}")

        for iid in self.top.get_children():
            self.top.delete(iid)
        for row in top_products():
            self.top.insert("", "end", values=(row["name"], row["qty_vendue"], f"{row['montant']:.2f}"))

        super().__init__(master, padding=8)
        ttk.Button(self, text="Rafraîchir rapports", command=self.refresh).pack(anchor="w", pady=(0, 8))
        self.summary = tk.Text(self, height=8, width=70)
        self.summary.pack(fill="x")

        ttk.Label(self, text="Top produits", font=("Arial", 11, "bold")).pack(anchor="w", pady=(12, 6))
        self.top = tk.Listbox(self, height=8)
        self.top.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self) -> None:
        self.summary.delete("1.0", "end")
        data = daily_sales_summary()
        self.summary.insert(
            "end",
            (
                f"Nombre ventes: {data['nb_ventes']}\n"
                f"Total HT: {data['total_ht']:.2f}\n"
                f"Total TVA: {data['total_tva']:.2f}\n"
                f"Total TTC: {data['total_ttc']:.2f}\n"
            ),
        )

        self.top.delete(0, "end")
        for row in top_products():
            self.top.insert("end", f"{row['name']} | qté={row['qty_vendue']} | montant={row['montant']:.2f}")
 main


class PharmacyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pharmacie POS - MVP")
 codex/propose-complete-cash-register-system-design-ah3cit
        self.geometry("1000x700")
        self.minsize(920, 620)

        configure_style(self)

        self.geometry("900x650")

 main
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
