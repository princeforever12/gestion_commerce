import tkinter as tk
from tkinter import messagebox, ttk

from pharmacy_pos.services.auth_service import User, authenticate
from pharmacy_pos.services.bootstrap_service import bootstrap
from pharmacy_pos.services.product_service import create_product, list_products
from pharmacy_pos.services.report_service import daily_sales_summary, top_products
from pharmacy_pos.services.sales_service import create_sale
from pharmacy_pos.services.stock_service import add_stock, get_low_stock_products


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

    def _submit(self) -> None:
        user = authenticate(self.username.get().strip(), self.password.get().strip())
        if user is None:
            messagebox.showerror("Erreur", "Identifiants invalides")
            return
        self.on_login(user)


class DashboardFrame(ttk.Frame):
    def __init__(self, master: tk.Tk, user: User):
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


class PosTab(ttk.Frame):
    def __init__(self, master, cashier_id: int):
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
        self.lines.insert("end", f"Produit #{product_id} x{quantity}")
        self.product_id_var.set("")
        self.quantity_var.set("1")

    def checkout(self) -> None:
        try:
            sale_id = create_sale(self.cashier_id, self.items, self.payment_var.get().strip())
        except Exception as exc:
            messagebox.showerror("Vente impossible", str(exc))
            return

        messagebox.showinfo("Succès", f"Vente enregistrée ID={sale_id}")
        self.items.clear()
        self.lines.delete(0, "end")


class StockTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=8)

        ttk.Label(self, text="Produits", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Button(self, text="Rafraîchir", command=self.refresh_products).grid(row=0, column=1, sticky="e")

        self.products = tk.Listbox(self, height=8)
        self.products.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(6, 12))

        add_product = ttk.LabelFrame(self, text="Nouveau produit")
        add_product.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))

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
        for idx, (label, var) in enumerate(fields):
            ttk.Label(add_product, text=label).grid(row=idx, column=0, sticky="w", padx=6, pady=2)
            ttk.Entry(add_product, textvariable=var, width=22).grid(row=idx, column=1, sticky="ew", padx=6, pady=2)

        ttk.Button(add_product, text="Créer produit", command=self.create_product_ui).grid(
            row=len(fields), column=0, columnspan=2, pady=8
        )
        add_product.columnconfigure(1, weight=1)

        add_stock_box = ttk.LabelFrame(self, text="Ajouter lot")
        add_stock_box.grid(row=3, column=0, columnspan=2, sticky="ew")
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


class PharmacyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pharmacie POS - MVP")
        self.geometry("900x650")

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
