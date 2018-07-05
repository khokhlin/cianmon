# Cianmon

Скрипт для мониторинга цен на квартиры на сайте cian.ru

## Установка

```
git clone https://github.com/khokhlin/cianmon && cd cianmon && python3 setup.py install
```

## Использование

--ids-file - файл со списком id объявлений.
--ids - список id объявлений.

Обновление цен:

```
cianmon update --ids-file=/tmp/flats.txt --ids 1 2 3
```

История изменений:

```
cianmon history --ids 1
```
