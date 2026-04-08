import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- تعديلات الأمان (مهمة للاستضافة) ---
# حاول دائماً جلب الـ Key من متغيرات البيئة، وإلا استخدم القيمة الافتراضية
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-jqpx=9#ded@(vm*1bplc8cpmikz*qa1=tszo8m_5$ks==avvn@')

# في الاستضافة يجب أن يكون DEBUG = False لكي لا ينهار السيرفر أو يسرب معلومات
DEBUG = os.environ.get('DEBUG', 'True') == 'True' 

# حدد الدومينات المسموح لها بتشغيل السيرفر (أضف رابط الـ backend الخاص بك)
ALLOWED_HOSTS = ['spark-peerlees.onrender.com', 'localhost', '127.0.0.1', '*']

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

# --- الميدل وير (الترتيب هنا حاسم جداً) ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # يجب أن يكون أولاً لمعالجة الطلبات الخارجية
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # لمعالجة الملفات الساكنة (CSS/Images)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'swarder_backend.urls'

# ... (جزء TEMPLATES يبقى كما هو في كودك)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- قاعدة البيانات ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- إعدادات الملفات الساكنة (ضرورية لـ Render) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# التخزين لـ Whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- إعدادات CORS (التصحيح النهائي) ---
CORS_ALLOW_ALL_ORIGINS = True # للتبسيط في البداية، أو استخدم CORS_ALLOWED_ORIGINS للخصوصية
CORS_ALLOW_CREDENTIALS = True
