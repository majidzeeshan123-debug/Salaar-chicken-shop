"""
Poultry Shop Management App
Run this file in Pydroid 3 (Kivy must be installed: pip install kivy).
Handles: Purchases, Processing (cutting), Sales (Live/Meat/Kaleji-Pota/Waste),
Expenses, Khata (credit ledger), Stock, and Daily History.
"""
from datetime import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window

from database import Database, CATEGORIES

db = Database()


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def show_popup(title, message):
    box = BoxLayout(orientation="vertical", padding=10, spacing=10)
    box.add_widget(Label(text=message))
    btn = Button(text="OK", size_hint_y=None, height=45)
    box.add_widget(btn)
    popup = Popup(title=title, content=box, size_hint=(0.85, 0.4))
    btn.bind(on_release=popup.dismiss)
    popup.open()


class TopBar(BoxLayout):
    """Reusable header with a title and a back-to-dashboard button."""
    def __init__(self, title, manager, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=50,
                          padding=5, spacing=5, **kwargs)
        back_btn = Button(text="< Dashboard", size_hint_x=None, width=140)
        back_btn.bind(on_release=lambda x: setattr(manager, "current", "dashboard"))
        self.add_widget(back_btn)
        self.add_widget(Label(text=title, font_size=20, bold=True))


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------
class DashboardScreen(Screen):
    def on_pre_enter(self, *args):
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)
        root.add_widget(Label(text="Poultry Shop - Hisab Kitab", font_size=24, bold=True,
                               size_hint_y=None, height=50))

        summary = db.get_summary_for_date(today_str())
        stats = GridLayout(cols=2, size_hint_y=None, height=160, spacing=5)
        for label, value in [
            ("Today's Purchase", summary["Total Purchase"]),
            ("Today's Sales", summary["Total Sales"]),
            ("Today's Expense", summary["Total Expense"]),
            ("Today's Net Profit", summary["Net Profit"]),
        ]:
            stats.add_widget(Label(text=label))
            stats.add_widget(Label(text=f"Rs. {value}", bold=True))
        root.add_widget(stats)

        menu = GridLayout(cols=2, spacing=10, size_hint_y=None)
        menu.bind(minimum_height=menu.setter("height"))
        buttons = [
            ("Purchase", "purchase"),
            ("Processing", "processing"),
            ("Sales", "sales"),
            ("Expenses", "expenses"),
            ("Khata (Credit)", "khata"),
            ("Stock", "stock"),
            ("History", "history"),
        ]
        for text, screen_name in buttons:
            btn = Button(text=text, size_hint_y=None, height=70, font_size=18)
            btn.bind(on_release=lambda x, s=screen_name: setattr(self.manager, "current", s))
            menu.add_widget(btn)

        scroll = ScrollView()
        scroll.add_widget(menu)
        root.add_widget(scroll)
        self.add_widget(root)


# ---------------------------------------------------------------------------
# PURCHASE
# ---------------------------------------------------------------------------
class PurchaseScreen(Screen):
    def on_pre_enter(self, *args):
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(TopBar("Purchase Live Chicken", self.manager))

        form = GridLayout(cols=2, size_hint_y=None, height=220, spacing=8)
        self.date_input = TextInput(text=today_str(), multiline=False)
        self.supplier_input = TextInput(hint_text="Supplier name", multiline=False)
        self.weight_input = TextInput(hint_text="Weight (KG)", multiline=False, input_filter="float")
        self.rate_input = TextInput(hint_text="Rate per KG (Rs.)", multiline=False, input_filter="float")
        self.notes_input = TextInput(hint_text="Notes (optional)", multiline=False)

        for label, widget in [("Date", self.date_input), ("Supplier", self.supplier_input),
                               ("Weight (KG)", self.weight_input), ("Rate/KG", self.rate_input),
                               ("Notes", self.notes_input)]:
            form.add_widget(Label(text=label))
            form.add_widget(widget)
        root.add_widget(form)

        self.total_label = Label(text="Total Cost: Rs. 0", font_size=18, bold=True,
                                  size_hint_y=None, height=40)
        root.add_widget(self.total_label)

        save_btn = Button(text="Save Purchase", size_hint_y=None, height=55, font_size=18)
        save_btn.bind(on_release=self.save)
        root.add_widget(save_btn)
        root.add_widget(BoxLayout())
        self.add_widget(root)

    def save(self, *args):
        try:
            weight = float(self.weight_input.text)
            rate = float(self.rate_input.text)
            supplier = self.supplier_input.text.strip() or "Unknown"
        except ValueError:
            show_popup("Error", "Please enter valid Weight and Rate.")
            return
        total = db.add_purchase(self.date_input.text, supplier, weight, rate, self.notes_input.text)
        self.total_label.text = f"Total Cost: Rs. {total}"
        show_popup("Saved", f"Purchase saved.\nTotal Cost: Rs. {total}")
        self.build()


# ---------------------------------------------------------------------------
# PROCESSING (cutting live chicken into meat / kaleji-pota / waste)
# ---------------------------------------------------------------------------
class ProcessingScreen(Screen):
    def on_pre_enter(self, *args):
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(TopBar("Processing (Cutting)", self.manager))
        root.add_widget(Label(
            text="Convert live chicken weight into Meat + Kaleji-Pota + Waste",
            size_hint_y=None, height=40, font_size=14))

        form = GridLayout(cols=2, size_hint_y=None, height=260, spacing=8)
        self.date_input = TextInput(text=today_str(), multiline=False)
        self.live_input = TextInput(hint_text="Live weight used (KG)", multiline=False, input_filter="float")
        self.meat_input = TextInput(hint_text="Meat produced (KG)", multiline=False, input_filter="float")
        self.kp_input = TextInput(hint_text="Kaleji-Pota produced (KG)", multiline=False, input_filter="float")
        self.waste_input = TextInput(hint_text="Waste produced (KG)", multiline=False, input_filter="float")
        self.notes_input = TextInput(hint_text="Notes (optional)", multiline=False)

        for label, widget in [("Date", self.date_input), ("Live Wt Used", self.live_input),
                               ("Meat Produced", self.meat_input), ("Kaleji-Pota", self.kp_input),
                               ("Waste", self.waste_input), ("Notes", self.notes_input)]:
            form.add_widget(Label(text=label))
            form.add_widget(widget)
        root.add_widget(form)

        save_btn = Button(text="Save Processing Entry", size_hint_y=None, height=55, font_size=18)
        save_btn.bind(on_release=self.save)
        root.add_widget(save_btn)
        root.add_widget(BoxLayout())
        self.add_widget(root)

    def save(self, *args):
        try:
            live = float(self.live_input.text)
            meat = float(self.meat_input.text or 0)
            kp = float(self.kp_input.text or 0)
            waste = float(self.waste_input.text or 0)
        except ValueError:
            show_popup("Error", "Please enter valid numbers.")
            return
        db.add_processing(self.date_input.text, live, meat, kp, waste, self.notes_input.text)
        show_popup("Saved", "Processing entry saved.")
        self.build()


# ---------------------------------------------------------------------------
# SALES
# ---------------------------------------------------------------------------
class SalesScreen(Screen):
    def on_pre_enter(self, *args):
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(TopBar("Sales", self.manager))

        form = GridLayout(cols=2, size_hint_y=None, height=300, spacing=8)
        self.date_input = TextInput(text=today_str(), multiline=False)
        self.category_spinner = Spinner(text=CATEGORIES[0], values=CATEGORIES)
        self.weight_input = TextInput(hint_text="Weight (KG)", multiline=False, input_filter="float")
        self.rate_input = TextInput(hint_text="Rate per KG (Rs.)", multiline=False, input_filter="float")
        self.customer_input = TextInput(hint_text="Customer name", multiline=False)
        self.payment_spinner = Spinner(text="Cash", values=["Cash", "Credit"])
        self.notes_input = TextInput(hint_text="Notes (optional)", multiline=False)

        for label, widget in [("Date", self.date_input), ("Category", self.category_spinner),
                               ("Weight (KG)", self.weight_input), ("Rate/KG", self.rate_input),
                               ("Customer", self.customer_input), ("Payment Type", self.payment_spinner),
                               ("Notes", self.notes_input)]:
            form.add_widget(Label(text=label))
            form.add_widget(widget)
        root.add_widget(form)

        self.total_label = Label(text="Total: Rs. 0", font_size=18, bold=True,
                                  size_hint_y=None, height=40)
        root.add_widget(self.total_label)

        save_btn = Button(text="Save Sale", size_hint_y=None, height=55, font_size=18)
        save_btn.bind(on_release=self.save)
        root.add_widget(save_btn)
        root.add_widget(BoxLayout())
        self.add_widget(root)

    def save(self, *args):
        try:
            weight = float(self.weight_input.text)
            rate = float(self.rate_input.text)
        except ValueError:
            show_popup("Error", "Please enter valid Weight and Rate.")
            return
        customer = self.customer_input.text.strip() or "Walk-in Customer"
        total = db.add_sale(self.date_input.text, self.category_spinner.text, weight, rate,
                             customer, self.payment_spinner.text, self.notes_input.text)
        self.total_label.text = f"Total: Rs. {total}"
        show_popup("Saved", f"Sale saved.\n{self.category_spinner.text}: Rs. {total}")
        self.build()


# ---------------------------------------------------------------------------
# EXPENSES
# ---------------------------------------------------------------------------
class ExpensesScreen(Screen):
    EXPENSE_CATEGORIES = ["Transport", "Labor", "Ice", "Electricity", "Rent", "Other"]

    def on_pre_enter(self, *args):
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(TopBar("Expenses", self.manager))

        form = GridLayout(cols=2, size_hint_y=None, height=180, spacing=8)
        self.date_input = TextInput(text=today_str(), multiline=False)
        self.category_spinner = Spinner(text=self.EXPENSE_CATEGORIES[0], values=self.EXPENSE_CATEGORIES)
        self.amount_input = TextInput(hint_text="Amount (Rs.)", multiline=False, input_filter="float")
        self.notes_input = TextInput(hint_text="Notes (optional)", multiline=False)

        for label, widget in [("Date", self.date_input), ("Category", self.category_spinner),
                               ("Amount", self.amount_input), ("Notes", self.notes_input)]:
            form.add_widget(Label(text=label))
            form.add_widget(widget)
        root.add_widget(form)

        save_btn = Button(text="Save Expense", size_hint_y=None, height=55, font_size=18)
        save_btn.bind(on_release=self.save)
        root.add_widget(save_btn)
        root.add_widget(BoxLayout())
        self.add_widget(root)

    def save(self, *args):
        try:
            amount = float(self.amount_input.text)
        except ValueError:
            show_popup("Error", "Please enter a valid amount.")
            return
        db.add_expense(self.date_input.text, self.category_spinner.text, amount, self.notes_input.text)
        show_popup("Saved", "Expense saved.")
        self.build()


# ---------------------------------------------------------------------------
# KHATA (credit ledger)
# ---------------------------------------------------------------------------
class KhataScreen(Screen):
    def on_pre_enter(self, *args):
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(TopBar("Khata (Credit Ledger)", self.manager))

        form = GridLayout(cols=2, size_hint_y=None, height=220, spacing=8)
        self.date_input = TextInput(text=today_str(), multiline=False)
        self.customer_input = TextInput(hint_text="Customer name", multiline=False)
        self.phone_input = TextInput(hint_text="Phone (optional)", multiline=False)
        self.type_spinner = Spinner(text="Payment Received", values=["Payment Received", "Credit Sale"])
        self.amount_input = TextInput(hint_text="Amount (Rs.)", multiline=False, input_filter="float")

        for label, widget in [("Date", self.date_input), ("Customer", self.customer_input),
                               ("Phone", self.phone_input), ("Entry Type", self.type_spinner),
                               ("Amount", self.amount_input)]:
            form.add_widget(Label(text=label))
            form.add_widget(widget)
        root.add_widget(form)

        save_btn = Button(text="Save Khata Entry", size_hint_y=None, height=55, font_size=18)
        save_btn.bind(on_release=self.save)
        root.add_widget(save_btn)

        root.add_widget(Label(text="Outstanding Balances", font_size=18, bold=True,
                               size_hint_y=None, height=35))
        self.list_layout = GridLayout(cols=2, size_hint_y=None, spacing=4)
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.refresh_list()
        scroll = ScrollView()
        scroll.add_widget(self.list_layout)
        root.add_widget(scroll)
        self.add_widget(root)

    def refresh_list(self):
        self.list_layout.clear_widgets()
        for customer, balance in db.get_khata_customers().items():
            self.list_layout.add_widget(Label(text=customer, size_hint_y=None, height=30))
            self.list_layout.add_widget(Label(text=f"Rs. {balance}", size_hint_y=None, height=30))

    def save(self, *args):
        try:
            amount = float(self.amount_input.text)
        except ValueError:
            show_popup("Error", "Please enter a valid amount.")
            return
        customer = self.customer_input.text.strip()
        if not customer:
            show_popup("Error", "Please enter a customer name.")
            return
        balance = db.add_khata_entry(self.date_input.text, customer, self.phone_input.text,
                                      self.type_spinner.text, amount)
        show_popup("Saved", f"{customer}'s new balance: Rs. {balance}")
        self.build()


# ---------------------------------------------------------------------------
# STOCK
# ---------------------------------------------------------------------------
class StockScreen(Screen):
    def on_pre_enter(self, *args):
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(TopBar("Current Stock", self.manager))

        stock = db.get_stock_summary()
        grid = GridLayout(cols=2, size_hint_y=None, spacing=8)
        grid.bind(minimum_height=grid.setter("height"))
        for name, qty in stock.items():
            grid.add_widget(Label(text=name, font_size=18))
            grid.add_widget(Label(text=str(qty), font_size=18, bold=True))
        root.add_widget(grid)
        root.add_widget(BoxLayout())
        self.add_widget(root)


# ---------------------------------------------------------------------------
# HISTORY
# ---------------------------------------------------------------------------
class HistoryScreen(Screen):
    def on_pre_enter(self, *args):
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(TopBar("History (by date)", self.manager))

        search_row = BoxLayout(size_hint_y=None, height=50, spacing=8)
        self.date_input = TextInput(text=today_str(), multiline=False)
        search_btn = Button(text="Search", size_hint_x=None, width=120)
        search_btn.bind(on_release=self.search)
        search_row.add_widget(self.date_input)
        search_row.add_widget(search_btn)
        root.add_widget(search_row)

        self.result_layout = GridLayout(cols=2, size_hint_y=None, spacing=4)
        self.result_layout.bind(minimum_height=self.result_layout.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.result_layout)
        root.add_widget(scroll)
        self.add_widget(root)
        self.search()

    def search(self, *args):
        self.result_layout.clear_widgets()
        summary = db.get_summary_for_date(self.date_input.text)
        rows = [
            ("Total Purchase", summary["Total Purchase"]),
            ("Total Sales", summary["Total Sales"]),
            ("Total Expense", summary["Total Expense"]),
            ("Net Profit", summary["Net Profit"]),
        ]
        for cat, amt in summary["Sales By Category"].items():
            rows.append((f"Sales - {cat}", amt))
        for label, value in rows:
            self.result_layout.add_widget(Label(text=label, size_hint_y=None, height=30))
            self.result_layout.add_widget(Label(text=f"Rs. {value}", size_hint_y=None, height=30))


# ---------------------------------------------------------------------------
# APP
# ---------------------------------------------------------------------------
class PoultryShopApp(App):
    def build(self):
        Window.clearcolor = (0.96, 0.96, 0.96, 1)
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(PurchaseScreen(name="purchase"))
        sm.add_widget(ProcessingScreen(name="processing"))
        sm.add_widget(SalesScreen(name="sales"))
        sm.add_widget(ExpensesScreen(name="expenses"))
        sm.add_widget(KhataScreen(name="khata"))
        sm.add_widget(StockScreen(name="stock"))
        sm.add_widget(HistoryScreen(name="history"))
        return sm


if __name__ == "__main__":
    PoultryShopApp().run()
