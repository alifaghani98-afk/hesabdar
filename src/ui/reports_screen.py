"""
reports_screen.py - Reports, summaries and Excel export screen.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp

from ..db import (get_all_projects, get_all_counterparties,
                  get_summary, get_all_summaries_by_project)
from ..utils.validators import format_amount
from ..utils.exporter import (export_full_system,
                               export_by_project,
                               export_by_counterparty)


class ReportsScreen(Screen):

    _projects       = []
    _counterparties = []

    def on_enter(self):
        self._projects       = get_all_projects()
        self._counterparties = get_all_counterparties()
        self._populate_export_spinners()
        self.refresh_summary()
        self._render_project_summaries()

    def _populate_export_spinners(self):
        self.ids.sp_export_project.values = [p['name'] for p in self._projects] or ['—']
        self.ids.sp_export_project.text   = (self._projects[0]['name']
                                             if self._projects else '—')
        self.ids.sp_export_cp.values = [c['name'] for c in self._counterparties] or ['—']
        self.ids.sp_export_cp.text   = (self._counterparties[0]['name']
                                        if self._counterparties else '—')

    def refresh_summary(self):
        s = get_summary()
        self.ids.rpt_total_debit.text  = f"جمع بدهکار: {format_amount(s['total_debit'])} ریال"
        self.ids.rpt_total_credit.text = f"جمع بستانکار: {format_amount(s['total_credit'])} ریال"
        bal = s['balance']
        sign = '' if bal == 0 else ('+' if bal > 0 else '-')
        self.ids.rpt_balance.text = f"مانده نهایی: {sign}{format_amount(abs(bal))} ریال"

    def _render_project_summaries(self):
        box = self.ids.project_summary_box
        # Remove previous rows (keep title)
        children_to_remove = box.children[:-1]
        for c in children_to_remove:
            box.remove_widget(c)

        summaries = get_all_summaries_by_project()
        for s in summaries:
            row = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(4))
            row.add_widget(Label(
                text=s['project_name'], font_name='Vazir',
                halign='right', text_size=(dp(120), None),
                color=(0.15, 0.15, 0.2, 1), font_size=dp(13)
            ))
            row.add_widget(Label(
                text=f"بد: {format_amount(s['total_debit'])}",
                font_name='Vazir', color=(0.83, 0.18, 0.18, 1), font_size=dp(12)
            ))
            row.add_widget(Label(
                text=f"بس: {format_amount(s['total_credit'])}",
                font_name='Vazir', color=(0.13, 0.63, 0.28, 1), font_size=dp(12)
            ))
            box.add_widget(row)
            box.height = dp(30 + 30 * len(summaries))

    # ─── Export handlers ─────────────────────────────────────────────────────
    def export_full(self):
        try:
            path = export_full_system()
            self._alert(f"فایل ذخیره شد:\n{path}")
        except Exception as e:
            self._alert(f"خطا در خروجی:\n{e}")

    def export_project(self):
        sel = self.ids.sp_export_project.text
        if not sel or sel == '—':
            self._alert('یک پروژه انتخاب کنید.')
            return
        proj = next((p for p in self._projects if p['name'] == sel), None)
        if not proj:
            self._alert('پروژه یافت نشد.')
            return
        try:
            path = export_by_project(proj['id'], proj['name'])
            self._alert(f"فایل ذخیره شد:\n{path}")
        except Exception as e:
            self._alert(f"خطا در خروجی:\n{e}")

    def export_counterparty(self):
        sel = self.ids.sp_export_cp.text
        if not sel or sel == '—':
            self._alert('یک طرف حساب انتخاب کنید.')
            return
        cp = next((c for c in self._counterparties if c['name'] == sel), None)
        if not cp:
            self._alert('طرف حساب یافت نشد.')
            return
        try:
            path = export_by_counterparty(cp['id'], cp['name'])
            self._alert(f"فایل ذخیره شد:\n{path}")
        except Exception as e:
            self._alert(f"خطا در خروجی:\n{e}")

    # ─── Alert popup ─────────────────────────────────────────────────────────
    def _alert(self, msg):
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        layout.add_widget(Label(
            text=msg, font_name='Vazir', halign='right',
            text_size=(dp(300), None), color=(0.15, 0.15, 0.2, 1)
        ))
        popup = Popup(title='پیام', content=layout,
                      size_hint=(0.9, None), height=dp(200))
        layout.add_widget(Button(
            text='باشه', font_name='Vazir',
            size_hint_y=None, height=dp(44),
            background_color=(0.13, 0.47, 0.71, 1),
            background_normal='', color=(1, 1, 1, 1),
            on_press=popup.dismiss
        ))
        popup.open()
