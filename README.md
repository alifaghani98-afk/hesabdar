# حسابدار — Persian Project-Based Accounting App
### Kivy + Python + SQLite | Offline-First | Android APK

---

## ساختار پروژه / Project Structure

```
hesabdar/
├── main.py                          # نقطه ورود برنامه
├── hesabdar.kv                      # تعریف رابط کاربری (Kivy Language)
├── buildozer.spec                   # تنظیمات ساخت APK اندروید
├── requirements.txt                 # کتابخانه‌های مورد نیاز
├── hesabdar.db                      # پایگاه داده SQLite (خودکار ساخته می‌شود)
│
├── assets/
│   └── fonts/
│       └── Vazir.ttf               # فونت فارسی وزیر
│
├── exports/                         # فایل‌های اکسل خروجی
│
└── src/
    ├── __init__.py
    │
    ├── db/                          # لایه پایگاه داده
    │   ├── __init__.py
    │   ├── database.py              # اتصال و ایجاد جداول
    │   ├── projects_dao.py          # عملیات CRUD پروژه‌ها
    │   ├── counterparties_dao.py    # عملیات CRUD طرف حساب‌ها
    │   └── transactions_dao.py      # عملیات CRUD + خلاصه تراکنش‌ها
    │
    ├── utils/                       # ابزارها و منطق کسب و کار
    │   ├── __init__.py
    │   ├── jalali_utils.py          # تبدیل و نمایش تاریخ شمسی
    │   ├── validators.py            # اعتبارسنجی ورودی
    │   └── exporter.py             # خروجی اکسل با pandas+openpyxl
    │
    └── ui/                          # صفحه‌های رابط کاربری
        ├── __init__.py
        ├── main_screen.py           # صفحه اصلی + نوار خلاصه
        ├── projects_screen.py       # مدیریت پروژه‌ها
        ├── counterparties_screen.py # مدیریت طرف حساب‌ها
        ├── transactions_screen.py   # ثبت و مدیریت تراکنش‌ها
        └── reports_screen.py        # گزارش‌ها و خروجی اکسل
```

---

## ۱. نصب فونت فارسی / Install Persian Font

دانلود فونت **وزیر** از:
https://github.com/rastikerdar/vazir-font/releases

فایل `Vazir.ttf` را در مسیر زیر قرار دهید:
```
hesabdar/assets/fonts/Vazir.ttf
```

---

## ۲. نصب پیش‌نیازها / Install Dependencies

```bash
# ایجاد محیط مجازی (پیشنهادی)
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# نصب کتابخانه‌ها
pip install -r requirements.txt
```

---

## ۳. اجرا روی دسکتاپ / Run on Desktop

```bash
cd hesabdar
python main.py
```

---

## ۴. ساخت APK اندروید / Build Android APK

### پیش‌نیازهای ساخت APK:
- سیستم‌عامل Linux (Ubuntu/Debian توصیه می‌شود)
- Python 3.8+
- Java JDK 17

### مراحل:

```bash
# ۱. نصب buildozer
pip install buildozer

# ۲. نصب وابستگی‌های سیستمی (Ubuntu)
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip \
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
    libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev \
    build-essential libsqlite3-dev

# ۳. رفتن به پوشه پروژه
cd hesabdar

# ۴. ساخت APK دیباگ (اولین بار ۱۵-۴۵ دقیقه طول می‌کشد)
buildozer android debug

# ۵. APK در این مسیر قرار می‌گیرد:
# hesabdar/.buildozer/android/platform/build-arm64-v8a/dists/hesabdar/build/outputs/apk/debug/
# یا خلاصه‌تر:
ls bin/
```

### نصب مستقیم روی گوشی (با USB):
```bash
buildozer android debug deploy run
```

---

## ۵. ویژگی‌های اصلی / Core Features

| ویژگی | توضیح |
|-------|--------|
| 📁 پروژه‌ها | ایجاد، ویرایش، حذف پروژه |
| 👤 طرف حساب‌ها | مدیریت اشخاص/شرکت‌ها |
| 💰 تراکنش‌ها | بدهکار/بستانکار با تاریخ شمسی خودکار |
| 📊 گزارش | خلاصه کل، بر اساس پروژه، بر اساس طرف حساب |
| 📥 اکسل | خروجی .xlsx با pandas+openpyxl |
| 🗓 تاریخ شمسی | دریافت خودکار از دستگاه با jdatetime |
| 📴 آفلاین | بدون نیاز به اینترنت - SQLite |

---

## ۶. قوانین تراکنش / Transaction Rules

- فقط یکی از بدهکار یا بستانکار می‌تواند مقدار داشته باشد
- هر دو فیلد نمی‌توانند همزمان پر باشند
- هر دو فیلد نمی‌توانند صفر باشند
- مبالغ باید مثبت باشند
- مانده = جمع بستانکار − جمع بدهکار

---

## ۷. پایگاه داده / Database Schema

```sql
CREATE TABLE projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    description TEXT    DEFAULT ''
);

CREATE TABLE counterparties (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT    NOT NULL UNIQUE,
    phone TEXT    DEFAULT '',
    note  TEXT    DEFAULT ''
);

CREATE TABLE transactions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id       INTEGER NOT NULL,
    counterparty_id  INTEGER NOT NULL,
    jalali_date      TEXT    NOT NULL,  -- YYYY-MM-DD
    description      TEXT    DEFAULT '',
    debit            REAL    NOT NULL DEFAULT 0,
    credit           REAL    NOT NULL DEFAULT 0,
    FOREIGN KEY (project_id)      REFERENCES projects(id)      ON DELETE CASCADE,
    FOREIGN KEY (counterparty_id) REFERENCES counterparties(id) ON DELETE CASCADE
);
```

---

## ۸. رفع اشکال رایج / Troubleshooting

| مشکل | راه‌حل |
|------|---------|
| فونت فارسی نمایش داده نمی‌شود | فایل `Vazir.ttf` را در `assets/fonts/` قرار دهید |
| `jdatetime` یافت نشد | `pip install jdatetime` |
| `pandas` یافت نشد | `pip install pandas openpyxl` |
| APK ساخته نمی‌شود | مطمئن شوید Java JDK 17 نصب است |
| خطای SDL2 در لینوکس | `sudo apt install libsdl2-dev libsdl2-image-dev` |

---

*ساخته شده با Python + Kivy | طراحی برای کاربران ایرانی*
