<div id="header" align="center">
<h5 align="center"><img src="https://github.com/A-V-tor/telethon-script/blob/main/assets/1.png"></h5>
<h5 align="center"><img src="https://github.com/A-V-tor/telethon-script/blob/main/assets/2.png"></h5>
<h5 align="center"><img src="https://github.com/A-V-tor/telethon-script/blob/main/assets/3.png"></h5>
<h5 align="center"><img src="https://github.com/A-V-tor/telethon-script/blob/main/assets/4.png"></h5>
</div>
<h1 align="center">Развертывание проекта</h1>

## Скачать проект

```
  git clone git@github.com:A-V-tor/telethon-script.git
```

```
  cd telethon-script
```

В корне проекта создать файл `.env`

```
    API_ID # взять отсюда https://my.telegram.org/ 
    API_HASH # взять отсюда https://my.telegram.org/
    SECRET_KEY # секрентый ключ для сессий

```
## Собрать докер образ

```
docker build -t telethon .
```

## Запустить контейнер

```
docker run -p 8000:8000 telethon
```
##  Перейти по адрессу http://127.0.0.1:8000

## Пример запроса товара

<div id="header" align="center">
<h5 align="center"><img src="https://github.com/A-V-tor/telethon-script/blob/main/assets/5.png"></h5>
</div>
