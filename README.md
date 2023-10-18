# <h2>Описание:</h2>
Foodgram - сервис для публикации рецептов.
<br>
<br>
<h2>Установка:</h2>
<h3>Клонировать репозиторий и перейти в него в командной строке:</h3>
<ul>
<li>git git@github.com:Stas-SV/foodgram-project-react.git

</ul>

<h3>Запустите проект:</h3>
<ul>
<li>docker-compose up --buld</li>
</ul>
<ul>
<li>Из директории backend выполните миграции "docker-compose exec backend python manage.py migrate".</li>
</ul>
<ul>
<li>Соберите статику "docker-compose exec backend python manage.py collectstatic.</li>    
</ul>
<ul>
<li>Заполните базу ингредиентами и тэгами "docker-compose exec backend python manage.py import start.</li>    
</ul>
<ul>
<li>Соберите статику "docker-compose exec backend python manage.py collectstatic ".</li>    
</ul>

<h3>Запустить проект:</h3>
<ul>
<li>http://127.0.0.1:8000/</li>
</ul>
<ul>
<li>Документация к API находится по адресу: http://localhost/api/docs/redoc.html</li>
</ul>
