# Мониторинг Акций (Django/Vue.js)

Находясь в директории проекта `traiding_project` запустить `docker-compose up`  
Фронтенд (Vue.js) доступен на `http://localhost:8080/`  
Бекенд (Django) `http://localhost:8000/`
В проект добавлен selenoid необходимо предварительно скачать контейнеры с браузерами исполнив файл `prepare_browsers.bash`

<pre><code>
#local.env (файл переменных окружения)  
DJANGO_SETTINGS_MODULE=trading.settings  
DJANGO_WSGI=trading.wsgi  
PYTHONUNBUFFERED=1  
DATABASE_URL=postgres://localdb:localdb@db:5432/localdb  
POSTGRES_USER=localdb  
POSTGRES_PASSWORD=localdb  
POSTGRES_DB=localdb  

REDIS_HOST=redis  
C_FORCE_ROOT=true  

SECRET_KEY==@ncgb%60i%044*9yu%*$^$55s+(-y#qj_+4ldra-syv!62yu@  
DEBUG=True  

DJANGO_ADMINISTRATOR_PASS=adminpass  
</code></pre>
