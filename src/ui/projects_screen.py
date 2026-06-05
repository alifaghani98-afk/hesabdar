"""
projects_screen.py - Projects list, add/edit/delete popup logic.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp

from ..db import (get_all_projects, create_project,
                  update_project, delete_project, get_project)
from ..utils.validators import validate_name_field


class ProjectsScreen(Screen):

    def on_enter(self):
        self.refresh()

    def refresh(self):
        projects = get_all_projects()
        self.ids.rv_projects.data = [
            {
                'project_id':   p['id'],
                'project_name': p['name'],
                'project_desc': p['description'] or '',
                'screen_ref':   self
            }
            for p in projects
        ]

    # ─── Add ─────────────────────────────────────────────────────────────────
    def open_add_project(self):
        self._show_form(title='پروژه جدید', project_id=None)

    # ─── Edit ────────────────────────────────────────────────────────────────
    def open_edit_project(self, project_id):
        p = get_project(project_id)
        if p:
            self._show_form(title='ویرایش پروژه', project_id=project_id,
                            name=p['name'], description=p['description'] or '')

    # ─── Delete confirmation ─────────────────────────────────────────────────
    def confirm_delete_project(self, project_id):
        p = get_project(project_id)
        if not p:
            return
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        layout.add_widget(Label(
            text=f"پروژه «{p['name']}» و تمام تراکنش‌های آن حذف شود؟",
            font_name='Vazir', halign='right', text_size=(dp(280), None),
            color=(0.15, 0.15, 0.2, 1)
        ))
        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        popup = Popup(title='تأیید حذف', content=layout,
                      size_hint=(0.88, None), height=dp(180))

        btn_yes = Button(text='حذف', background_color=(0.83, 0.18, 0.18, 1),
                         background_normal='', color=(1, 1, 1, 1), font_name='Vazir')
        btn_no  = Button(text='انصراف', font_name='Vazir')
        btn_yes.bind(on_press=lambda *_: self._do_delete(project_id, popup))
        btn_no.bind(on_press=popup.dismiss)
        btns.add_widget(btn_yes)
        btns.add_widget(btn_no)
        layout.add_widget(btns)
        popup.open()

    def _do_delete(self, project_id, popup):
        delete_project(project_id)
        popup.dismiss()
        self.refresh()
        self._notify_app()

    # ─── Form popup ──────────────────────────────────────────────────────────
    def _show_form(self, title, project_id=None, name='', description=''):
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))

        ti_name = TextInput(text=name, hint_text='نام پروژه',
                            font_name='Vazir', halign='right',
                            multiline=False, size_hint_y=None, height=dp(44))
        ti_desc = TextInput(text=description, hint_text='توضیحات (اختیاری)',
                            font_name='Vazir', halign='right',
                            multiline=True, size_hint_y=None, height=dp(72))
        lbl_err = Label(text='', color=(0.83, 0.18, 0.18, 1),
                        font_name='Vazir', halign='right',
                        text_size=(dp(280), None),
                        size_hint_y=None, height=dp(40))

        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        popup = Popup(title=title, content=layout,
                      size_hint=(0.92, None), height=dp(300))

        def save(_):
            errs = validate_name_field(ti_name.text, 'نام پروژه')
            if errs:
                lbl_err.text = '\n'.join(errs)
                return
            try:
                if project_id is None:
                    create_project(ti_name.text, ti_desc.text)
                else:
                    update_project(project_id, ti_name.text, ti_desc.text)
                popup.dismiss()
                self.refresh()
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

        layout.add_widget(ti_name)
        layout.add_widget(ti_desc)
        layout.add_widget(lbl_err)
        layout.add_widget(btns)
        popup.open()

    def _notify_app(self):
        """Tell the root app to refresh the global summary bar."""
        try:
            self.manager.parent.parent.refresh_summary()
        except Exception:
            pass
