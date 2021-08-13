from environs import Env
from pathlib import Path

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
PAYMENT_PROVIDER_TOKEN = env.str('PAYMENT_PROVIDER_TOKEN')
# ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
IP = env.str("ip")  # Тоже str, но для айпи адреса хоста

I18N_DOMAIN = 'swipebot'
BASE_DIR = Path(__file__).parent.parent
LOCALES_DIR = Path.joinpath(BASE_DIR, 'locales')
DEBUG = int(env.str('DEBUG'))
if DEBUG == 1:
    REDIS_HOST = 'localhost'
else:
    REDIS_HOST = env.str('REDIS_HOST')
