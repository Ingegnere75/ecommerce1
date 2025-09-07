import os
from pathlib import Path
from dotenv import load_dotenv

# === BASE DIR ===
BASE_DIR = Path(__file__).resolve().parent.parent

# Carica variabili da .env (posto nella root del progetto)
load_dotenv(BASE_DIR / ".env")

# Utility per leggere liste CSV dalle env (es. "a,b,c")
def _csv(name: str, default: str = ""):
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]

# === SICUREZZA ===
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me-in-prod")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = _csv(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost"
)

CSRF_TRUSTED_ORIGINS = _csv(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://127.0.0.1,http://localhost"
)

# === APP INSTALLATE ===
INSTALLED_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "django_ckeditor_5",  # CKEditor 5
    "widget_tweaks",
    "django_extensions",

    "contentcollector",
    "requesttracker",
    "logmanager",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # App personalizzate
    "chatbot",
    "blog",
    "core",
    "accounts",
    "adminpanel",
    "amministratore",
]

# === MIDDLEWARE ===
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "amministratore.middleware.email_loop_blocker.EmailLoopBlockerMiddleware",
    "amministratore.middleware.maintenance_middleware.MaintenanceModeMiddleware",
    "middleware.blocco_globale.BloccoAccessoGlobaleMiddleware",
    # Middleware personalizzati
    "negozio.middleware.ContentCollectorMiddleware",
    "negozio.middleware.LogMiddleware",
    "negozio.middleware.SessionStrictMiddleware",
    "negozio.middleware.AutoLogoutMiddleware",
    "negozio.middleware.BloccaAccessoAdminManualeMiddleware",
]

# === URL & WSGI ===
ROOT_URLCONF = "negozio.urls"
WSGI_APPLICATION = "negozio.wsgi.application"

# === TEMPLATE ===
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                # Context processors personalizzati
                "core.context_processors.striscia_info",
                "core.context_processors.brand_context",
                "core.context_processors.contatti_brand_context",
                "core.context_processors.carrello_context",
            ],
        },
    },
]

# === DATABASE (SQLite di default) ===
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# === PASSWORD VALIDATION ===
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# === LINGUA & TEMPO ===
LANGUAGE_CODE = "it-it"
TIME_ZONE = "Europe/Rome"
USE_I18N = True
USE_TZ = True

# === STATIC & MEDIA ===
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === AUTO FIELD ===
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === CRISPY FORMS ===
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# === SESSIONE & SICUREZZA SESSIONI ===
SESSION_EXPIRE_SECONDS = int(os.getenv("SESSION_EXPIRE_SECONDS", "1800"))
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_TIMEOUT_REDIRECT = "/login/"
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = SESSION_EXPIRE_SECONDS
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in ("1", "true", "yes")
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

# === EMAIL ===
# In sviluppo usa console backend; in produzione configura SMTP via .env
if os.getenv("EMAIL_BACKEND", "").strip():
    EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend" if DEBUG else "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("1", "true", "yes")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "no-reply@example.com")
ADMINS = [("Admin", os.getenv("ADMIN_EMAIL", EMAIL_HOST_USER or "admin@example.com"))]

# === LOGIN REDIRECTS ===
LOGIN_REDIRECT_URL = "/accounts/dashboard/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# === CKEDITOR 5 CONFIG ===
CKEDITOR_5_CONFIGS = {
    "default": {
        "language": "it",
        "toolbar": [
            "heading", "|",
            "bold", "italic", "link", "underline", "bulletedList", "numberedList", "|",
            "blockQuote", "insertTable", "mediaEmbed", "|",
            "undo", "redo", "|",
            "imageUpload", "htmlEmbed",
        ],
        "image": {"toolbar": ["imageTextAlternative", "imageStyle:full", "imageStyle:side"]},
        "table": {"contentToolbar": ["tableColumn", "tableRow", "mergeTableCells"]},
        "mediaEmbed": {"previewsInData": True},
    }
}

# === STRIPE (se usi pagamenti) ===
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")

# === TWILIO (se usi SMS) ===
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# === MONGO (opzionale) ===
# Inserisci in .env: MONGODB_URI=mongodb+srv://user:pass@cluster/dbname?options...
from mongoengine import connect
MONGODB_URI = os.getenv("MONGODB_URI", "")
if MONGODB_URI:
    connect(host=MONGODB_URI)

# === UPLOAD LIMITS ===
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv("DATA_UPLOAD_MAX_MEMORY_SIZE", str(1024 * 1024 * 1024)))  # 1 GB
