"""
counterparties_screen.py - Counterparties CRUD UI.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp

from ..db import (get_all_counterparties, get_counterparty,
                  create_counterparty, update_counterparty, delete_counterparty)
from ..utils.validators import validate_name_field


class CounterpartiesScreen(Screen):

    def on_enter(self):
        self.refresh()

    def refresh(self):
        cps = get_all_counterparties()
        self.ids.rv_counterparties.data = [
            {
                'cp_id':    c['id'],
                'cp_name':  c['name'],
                'cp_phone': c['phone'] or '',
                'screen_ref': self
            }
            for c in cps
        ]

    def open_add_counterparty(self):
        self._show_form(title='طرف حساب جدید')

    def open_edit_counterparty(self, cp_id):
        c = get_counterparty(cp_id)
        if c:
            self._show_form(title='ویرایش طرف حساب', cp_id=cp_id,
                            name=c['name'], phone=c['phone'] or '',
                            note=c['note'] or '')

    def confirm_delete_counterparty(self, cp_id):
        c = get_counterparty(cp_id)
        if not c:
            return
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        layout.add_widget(Label(
            text=f"طرف حساب «{c['name']}» حذف شود؟",
            font_name='Vazir', halign='right',
            text_size=(dp(280), None), color=(0.15, 0.15, 0.2, 1)
        ))
        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        popup = Popup(title='تأیید حذف', content=layout,
                      size_hint=(0.88, None), height=dp(160))

        btn_yes = Button(text='حذف', background_color=(0.83, 0.18, 0.18, 1),
                         background_normal='', color=(1, 1, 1, 1), font_name='Vazir')
        btn_no  = Button(text='انصراف', font_name='Vazir')
        btn_yes.bind(on_press=lambda *_: self._do_delete(cp_id, popup))
        btn_no.bind(on_press=popup.dismiss)
        btns.add_widget(btn_yes)
        btns.add_widget(btn_no)
        layout.add_widget(btns)
        popup.open()

    def _do_delete(self, cp_id, popup):
        delete_counterparty(cp_id)
        popup.dismiss()
        self.refresh()

    def _show_form(self, title, cp_id=None, name='', phone='', note=''):
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        ti_name  = TextInput(text=name,  hint_text='نام طرف حساب',
                             font_name='Vazir', halign='right',
                             multiline=False, size_hint_y=None, height=dp(44))
        ti_phone = TextInput(text=phone, hint_text='شماره تلفن (اختیاری)',
                             font_name='Vazir', halign='right', input_type='number',
                             multiline=False, size_hint_y=None, height=dp(44))
        ti_note  = TextInput(text=note,  hint_text='یادداشت (اختیاری)',
                             font_name='Vazir', halign='right',
                             multiline=True, size_hint_y=None, height=dp(64))
        lbl_err  = Label(text='', color=(0.83, 0.18, 0.18, 1), font_name='Vazir',
                         halign='right', text_size=(dp(280), None),
                         size_hint_y=None, height=dp(40))
        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        popup = Popup(title=title, content=layout,
                      size_hint=(0.92, None), height=dp(340))

        def save(_):
            errs = validate_name_field(ti_name.text, 'نام طرف حساب')
            if errs:
                lbl_err.text = '\n'.join(errs)
                return
            try:
                if cp_id is None:
                    create_counterparty(ti_name.text, ti_phone.text, ti_note.text)
                else:
                    update_counterparty(cp_id, ti_name.text, ti_phone.text, ti_note.text)
                popup.dismiss()
                self.refresh()
            except Exception as e:
                lbl_err.text = f'خطا: {e}'

        btn_save   = Button(text='ذخیره', background_color=(0.13, 0.47, 0.71, 1),
                            background_normal='', color=(1, 1, 1, 1), font_name='Vazir')
        btn_cancel = Button(text='انصراف', font_name='Vazir')
        btn_save.bind(on_press=save)
        btn_cancel.bind(on_press=popup.dismiss)
        btns.add_widget(btn_save)
        btns.add_widget(btn_cancel)

        for w in (ti_name, ti_phone, ti_note, lbl_err, btns):
            layout.add_widget(w)
        popup.open()
