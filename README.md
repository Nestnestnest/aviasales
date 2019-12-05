# aviasales

В папке два XML – это ответы на поисковые запросы, сделанные к одному из наших партнёров.
В ответах лежат варианты перелётов (тег `Flights`) со всей необходимой информацией,
чтобы отобразить билет на Aviasales.

На основе этих данных, нужно сделать вебсервис,
в котором есть эндпоинты, отвечающие на следующие запросы:

* Какие варианты перелёта из DXB в BKK мы получили?
* Самый дорогой/дешёвый, быстрый/долгий и оптимальный варианты
* В чём отличия между результатами двух запросов (изменение маршрутов/условий)?

Язык реализации: `Go`
Формат ответа: `json`
По возможности использовать стандартную библиотеку.

Язык реализации: `python3`
Формат ответа: `json`
Используемые библиотеки и инструменты — всё на твой выбор.

Оценивать будем умение выполнять задачу имея неполные данные о ней,
умение самостоятельно принимать решения и качество кода.

#Решение
1. Есть возможность выводить рядом с временем вылета/прилета локальное время клиента по timezone (default='Europe/Moscow')
2. Цены конвертируются в валюту, которая соответствует timezone клиента (по России в RUB и т.п)
3. При обработке запроса выводятся все варианты перелета (при необходимости выводить отдельно __Самый дорогой/дешёвый, быстрый/долгий и оптимальный варианты__) добавлю отдельные эндпоинты) - сейчас ключевые варианты помечены соответствующими тегами
4. Добавил возможность отображения оптимального маршрута отдельно по цене/времени (при необходимости)
5. Добавил возможность просмотра ключевых вариантов в разрезе перелета (отдельно самый долгий перелет туда, самый дешевый перелет обратно) (при необходимости) P.S. Добавил т.к. для меня были бы актуальны варианты с тяжелым маршрутом туда (долгий перелет/пересадки) и быстрый перелет обратно
6. XML парсятся при каждом запросе, а не сохраняются (при необходимости)
7. В Redis хранятся __iata_code__ - справочник iata_code:country (для пункта 1),__timezone_country__  - timezone:country (для пункта 2 )

Для запуска через __docker-compose__ (http://0.0.0.0:8080):
```bash
$ docker-compose build
$ docker-compose up -d
```
Для запуска, без использование docker-compose:
```bash
$ redis-server
```
В файле avia_app/application.py заменить:
```python
# redis_client = FlaskRedis(host='redis')
redis_client = FlaskRedis()
'''в create_app() закомментировать:'''
# app.config['REDIS_URL'] = 'redis://redis/0'
```
