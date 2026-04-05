import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- تعديلات الأمان ---
SECRET_KEY = 'django-insecure-jqpx=9#ded@(vm*1bplc8cpmikz*qa1=tszo8m_5$ks==avvn@'
DEBUG = False # عطل الـ Debug في الاستضافة
ALLOWED_HOSTS = ['*'] # سيتم تخصيصه لاحقاً لدومينك

# --- التطبيقات ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core',
]

# --- الميدل وير (أضف WhiteNoise هنا) ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # أضفه هنا للتعامل مع الملفات الساكنة
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'swarder_backend.urls'

# --- قاعدة البيانات (SQLite حالياً) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- إعدادات الملفات الساكنة (مهمة جداً لـ Render) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# باقي الإعدادات (CORS, REST_FRAMEWORK) كما هي لديك...
