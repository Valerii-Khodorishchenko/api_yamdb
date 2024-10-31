# api_yamdb

## Описание
Проект YaMDb собирает отзывы пользователей на различные произведения.

## Установка
Для установки и запустить проекта локально, следуйте этим шагам:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Valerii-Khodorishchenko/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 yatube_api/manage.py migrate
```

Запустить проект:

```
python3 yatube_api/manage.py runserver
```
