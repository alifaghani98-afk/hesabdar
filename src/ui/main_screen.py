"""
main_screen.py - Root screen with tab navigation and summary bar.
"""
from kivy.uix.screenmanager import Screen
from ..db.transactions_dao import get_summary
from ..utils.validators import format_amount


class MainScreen(Screen):

    def on_kv_post(self, base_widget):
        self.refresh_summary()

    def show_tab(self, name):
        self.ids.sm.current = name
        # Refresh summary whenever tab changes
        self.refresh_summary()

    def refresh_summary(self):
        s = get_summary()
        d  = s['total_debit']
        cr = s['total_credit']
        bl = s['balance']

        self.ids.lbl_debit.text   = f"بدهکار: {format_amount(d)}"
        self.ids.lbl_credit.text  = f"بستانکار: {format_amount(cr)}"
        sign = '' if bl == 0 else ('+' if bl > 0 else '-')
        self.ids.lbl_balance.text = f"مانده: {sign}{format_amount(abs(bl))}"
