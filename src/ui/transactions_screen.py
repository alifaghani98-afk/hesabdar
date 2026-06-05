"""
transactions_screen.py - Transactions list with filter + add/edit/delete popup.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.metrics import dp

from ..db import (get_all_projects, get_all_counterparties,
                  get_transactions, get_transaction,
                  create_transaction, update_transaction, delete_transaction)
from ..utils.jalali_utils import today_jalali, format_jalali_display
from ..utils.validators import validate_transaction


class TransactionsScreen(Screen):

    _projects      = []
    _counterparties = []

    def on_enter(self):
        self._projects       = get_all_projects()
        self._counterparties = get_all_counterparties()
        self._populate_spinners()
        self.apply_filters()

    def _populate_spinners(self):
        proj_values = ['همه پروژه‌ها'] + [p['name'] for p in self._projects]
        cp_values   = ['همه طرف حساب‌ها'] + [c['name'] for c in self._counterparties]
        self.ids.sp_filter_project.values = proj_values
        self.ids.sp_filter_project.text   = 'همه پروژه‌ها'
        self.ids.sp_filter_cp.values      = cp_values
        self.ids.sp_filter_cp.text        = 'همه طرف حساب‌ها'

    def apply_filters(self):
        sel_proj = self.ids.sp_filter_project.text
        sel_cp   = self.ids.sp_filter_cp.text

        proj_id = None
        for p in self._projects:
            if p['name'] == sel_proj:
                proj_id = p['id']
                break

        cp_id = None
        for c in self._counterparties:
            if c['name'] == sel_cp:
                cp_id = c['id']
                break

        txs = get_transactions(project_id=proj_id, counterparty_id=cp_id)
        data = []
        for idx, t in enumerate(txs, start=1):
            data.append({
                'tx_id':      t['id'],
                'tx_row':     idx,
                'tx_date':    format_jalali_display(t['jalali_date']),
                'tx_desc':    t['description'],
                'tx_debit':   t['debit'],
                'tx_credit':  t['credit'],
                'tx_project': t.get('project_name', ''),
                'tx_cp':      t.get('counterparty_name', ''),
                'screen_ref': self
            })
        self.ids.rv_transactions.data = data

    # ─── Add ─────────────────────────────────────────────────────────────────
    def open_add_transaction(self):
        self._show_form(title='تراکنش جدید')

    # ─── Edit ────────────────────────────────────────────────────────────────
    def open_edit_transaction(self, tx_id):
        t = get_transaction(tx_id)
        if t:
            self._show_form(title='ویرایش تراکنش', tx_id=tx_id,
                            project_id=t['project_id'],
                            counterparty_id=t['counterparty_id'],
                            jalali_date=t['jalali_date'],
                            description=t['description'],
                            debit=t['debit'], credit=t['credit'])

    # ─── Delete ───────────────────────────────────────────────────────────────
    def confirm_delete_transaction(self, tx_id):
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        layout.add_widget(Label(
            text='این تراکنش حذف شود؟',
            font_name='Vazir', halign='right',
            text_size=(dp(280), None), color=(0.15, 0.15, 0.2, 1)
        ))
        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        popup = Popup(title='تأیید حذف', content=layout,
                      size_hint=(0.85, None), height=dp(150))
        btn_yes = Button(text='حذف', background_color=(0.83, 0.18, 0.18, 1),
                         background_normal='', color=(1, 1, 1, 1), font_name='Vazir')
        btn_no  = Button(text='انصراف', font_name='Vazir')
        btn_yes.bind(on_press=lambda *_: self._do_delete(tx_id, popup))
        btn_no.bind(on_press=popup.dismiss)
        btns.add_widget(btn_yes)
        btns.add_widget(btn_no)
        layout.add_widget(btns)
        popup.open()

    def _do_delete(self, tx_id, popup):
        delete_transaction(tx_id)
        popup.dismiss()
        self.apply_filters()
        self._notify_app()

    # ─── Form popup ──────────────────────────────────────────────────────────
    def _show_form(self, title, tx_id=None,
                   project_id=None, counterparty_id=None,
                   jalali_date=None, description='',
                   debit=0.0, credit=0.0):

        projects      = get_all_projects()
        counterparties = get_all_counterparties()

        if not projects:
            self._alert('ابتدا یک پروژه ایجاد کنید.')
            return
        if not counterparties:
            self._alert('ابتدا یک طرف حساب ایجاد کنید.')
            return

        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        # Project spinner
        sp_proj = Spinner(
            text=(next((p['name'] for p in projects if p['id'] == project_id), projects[0]['name'])),
            values=[p['name'] for p in projects],
            font_name='Vazir', size_hint_y=None, height=dp(44)
        )

        # Counterparty spinner
        sp_cp = Spinner(
            text=(next((c['name'] for c in counterparties if c['id'] == counterparty_id), counterparties[0]['name'])),
            values=[c['name'] for c in counterparties],
            font_name='Vazir', size_hint_y=None, height=dp(44)
        )

        # Date row
        date_row    = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        ti_date     = TextInput(
            text=jalali_date or today_jalali(),
            hint_text='YYYY-MM-DD', font_name='Vazir',
            halign='right', multiline=False,
            size_hint_y=None, height=dp(44), readonly=True
        )
        btn_edit_date = ToggleButton(
            text='ویرایش تاریخ', font_name='Vazir',
            size_hint_x=None, width=dp(110),
            size_hint_y=None, height=dp(44)
        )

        def toggle_date_edit(btn):
            ti_date.readonly = (btn.state != 'down')

        btn_edit_date.bind(on_press=toggle_date_edit)
        date_row.add_widget(ti_date)
        date_row.add_widget(btn_edit_date)

        # Description
        ti_desc = TextInput(
            text=description, hint_text='شرح تراکنش',
            font_name='Vazir', halign='right',
            multiline=False, size_hint_y=None, height=dp(44)
        )

        # Amount + type row
        amount_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        initial_amount = str(int(debit)) if debit > 0 else (str(int(credit)) if credit > 0 else '')
        ti_amount = TextInput(
            text=initial_amount,
            hint_text='مبلغ', font_name='Vazir',
            halign='right', input_type='number',
            multiline=False, size_hint_y=None, height=dp(44)
        )
        initial_type  = 'expense' if debit > 0 else 'income'
        sp_type = Spinner(
            text=('بدهکار (هزینه)' if initial_type == 'expense' else 'بستانکار (درآمد)'),
            values=['بدهکار (هزینه)', 'بستانکار (درآمد)'],
            font_name='Vazir', size_hint_y=None, height=dp(44)
        )
        amount_row.add_widget(ti_amount)
        amount_row.add_widget(sp_type)

        lbl_err = Label(
            text='', color=(0.83, 0.18, 0.18, 1),
            font_name='Vazir', halign='right',
            text_size=(dp(300), None), size_hint_y=None, height=dp(50)
        )

        btns = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        popup = Popup(title=title, content=layout,
                      size_hint=(0.95, None), height=dp(480))

        def save(_):
            # Resolve project/counterparty IDs
            pid = next((p['id'] for p in projects if p['name'] == sp_proj.text), None)
            cid = next((c['id'] for c in counterparties if c['name'] == sp_cp.text), None)

            is_expense = 'بدهکار' in sp_type.text
            amt_str    = ti_amount.text.strip()
            d_str      = amt_str if is_expense else '0'
            c_str      = amt_str if not is_expense else '0'

            errs = validate_transaction(d_str, c_str, ti_date.text, pid, cid)
            if errs:
                lbl_err.text = '\n'.join(errs)
                return

            try:
                d_val = float(amt_str) if is_expense else 0.0
                c_val = float(amt_str) if not is_expense else 0.0
                if tx_id is None:
                    create_transaction(pid, cid, ti_date.text,
                                       ti_desc.text, d_val, c_val)
                else:
                    update_transaction(tx_id, pid, cid, ti_date.text,
                                       ti_desc.text, d_val, c_val)
                popup.dismiss()
                self._projects       = get_all_projects()
                self._counterparties = get_all_counterparties()
                self.apply_filters()
                self._notify_app()
            except Exception as e:
                lbl_err.text = f'خطا: {e}'

        btn_save   = Button(text='ذخیره', background_color=(0.13, 0.47, 0.71, 1),
                            background_normal='', color=(1, 1, 1, 1), font_name='Vazir')
        btn_cancel = Button(text='انصراف', font_name='Vazir')
        btn_save.bind(on_press=save)
        btn_cancel.bind(on_press=popup.dismiss)
        btns.add_widget(btn_save)
        btns.add_widget(btn_cancel)

        for w in (sp_proj, sp_cp, date_row, ti_desc, amount_row, lbl_err, btns):
            layout.add_widget(w)
        popup.open()

    def _alert(self, msg):
        layout = BoxLayout(orientation='vertical', padding=dp(12))
        layout.add_widget(Label(text=msg, font_name='Vazir', halign='right',
                                text_size=(dp(280), None)))
        popup = Popup(title='توجه', content=layout,
                      size_hint=(0.85, None), height=dp(140))
        layout.add_widget(Button(text='باشه', font_name='Vazir',
                                 size_hint_y=None, height=dp(44),
                                 on_press=popup.dismiss))
        popup.open()

    def _notify_app(self):
        try:
            self.manager.parent.parent.refresh_summary()
        except Exception:
            pass
