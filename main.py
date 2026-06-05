"""
main.py - Application entry point.

Run on desktop : python main.py
Build APK      : buildozer android debug
"""
import os
import sys

# ── Ensure the project root is on the Python path ────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Kivy environment settings (must come BEFORE kivy imports) ─────────────────
os.environ.setdefault('KIVY_NO_CONSOLELOG', '0')

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from src.db.database import init_db
from src.ui import (MainScreen, ProjectsScreen, CounterpartiesScreen,
                    TransactionsScreen, ReportsScreen)


# ── Register Persian font ─────────────────────────────────────────────────────
FONT_PATH = os.path.join(ROOT, 'assets', 'fonts', 'Vazir.ttf')
if os.path.exists(FONT_PATH):
    LabelBase.register(name='Vazir', fn_regular=FONT_PATH)
else:
    # Fallback: use system default (Persian text may not render correctly)
    LabelBase.register(name='Vazir', fn_regular=LabelBase._fonts['Roboto']['fn_regular'])


class HesabdarApp(App):
    title = 'حسابدار'

    def build(self):
        init_db()
        Builder.load_file(os.path.join(ROOT, 'hesabdar.kv'))
        return MainScreen(name='main')

    def on_start(self):
        pass

    def on_stop(self):
        pass


if __name__ == '__main__':
    HesabdarApp().run()
