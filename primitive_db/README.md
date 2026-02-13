# Примитивная база данных на Python

Учебный проект: «движок» для работы с табличными данными (упрощённая СУБД) на Python.

Поддерживается хранение таблиц в файлах, базовый CRUD, кэширование выборки и простой парсер команд в стиле SQL.

## Установка

Через Poetry:

```bash
poetry install

или через Makefile:

make install
```
## Запуск
```bash
poetry run project
# или
make project
```

При старте вы увидите:

Введите 'help' для списка доступных команд.
>>>

### Команды
help выводит краткую справку:

### Доступные команды:
  list
      Показать список таблиц.
  help
      Показать эту справку.
  create <table> col:type ...
      Создать таблицу с указанными колонками и типами.
      Пример: create users id:int name:str age:int
  insert <table> field=value ...
      Добавить строку в таблицу.
      Пример: insert users name=Alice age=30
  select <table>
      Показать все строки таблицы (с кэшем).
      Пример: select users
  select <table> where field=value
      Показать строки, удовлетворяющие условию по одному полю.
      Пример: select users where age=30
  update <table> set field=value ... where id=VALUE
      Обновить строку по id.
      Пример: update users set age=31 where id=1
  delete <table> where id=VALUE
      Удалить строку по id (с подтверждением).
      Пример: delete users where id=1
  drop <table>
      Удалить таблицу целиком (с подтверждением).
      Пример: drop users
  describe <table>
      Показать схему таблицы (имена и типы колонок).
      Пример: describe users
  exit
      Выйти из программы.

### Алиасы:

ls → list
q → exit

### Возможности

Создание таблиц с явным описанием колонок и типов.

Добавление, выборка, обновление и удаление строк (CRUD).

Автоинкрементный ID для каждой таблицы.

Типы колонок: int, str.

Файловое хранение схемы и данных (data/*.json).

Кэширование результатов SELECT с инвалидацией при изменениях.

Декораторы:

    handle_db_errors — обработка ошибок.

    confirm_action — подтверждение опасных действий (delete, drop).

    log_time — логирование времени выполнения.

Парсер строковых команд с объектом Command.

Простая псевдо-SQL консоль.

### Стек

Python 3.12

Poetry для управления зависимостями.

Стандартная библиотека (dataclasses, typing, functools и др.).

prettytable для вывода таблиц.

## Архитектура

primitive_db/core.py — логика работы с таблицами и строками:

    create_table, drop_table, list_tables;

    insert_row, select_rows, select_rows_cached;

    update_row_by_id, delete_row_by_id;

    кэш select через замыкание и _SELECT_CACHE.

primitive_db/engine.py — работа с файлами и метаданными:

    load_db_meta, save_db_meta;

    load_table_data, save_table_data.

primitive_db/parser.py — парсер строковых команд:

    Command (тип команды, имя таблицы, значения, условия where/set);

    parse_command(line: str) -> Command.

primitive_db/decorators.py — общие декораторы:

    handle_db_errors — перехват ValueError и аккуратный вывод;

    confirm_action — запрос подтверждения перед delete/drop;

    log_time — измерение и вывод времени выполнения.

primitive_db/constants.py — пути к файлам, имя ID‑колонки, поддерживаемые типы.

primitive_db/utils.py — вспомогательные функции для ввода и вывода сообщений.

primitive_db/main.py — CLI-интерфейс:

    цикл чтения команд;

    dispatch_command(command: Command) — диспетчер по типу команды.

tests/test_parser.py — юнит‑тесты на парсер команд.

Проект проходит проверку mypy и ruff для основных модулей.

### Проверка стиля и типов

```bash
make lint
```
Выполнит ruff и mypy для пакета primitive_db и тестов.

## Демонстрация

Полный сеанс работы (создание таблицы, все CRUD‑операции, работа декоратора `confirm_action` и удаление таблицы) записан в asciinema:

[![asciinema demo](https://asciinema.org/a/G3LqeL2dRwYkYfKj.svg)](https://asciinema.org/a/G3LqeL2dRwYkYfKj)