# repos_dependency_graph

Веб-приложение для визуализации зависимостей rpm-пакетов в виде графа. 

Позволяет:

- Просматривать зависимости между пакетами
- Добавлять пакет в отслеживаемые
- Смотреть разницу графов между версиями 

Интерфейс реализован на Vue 3 + Vite.
Бэкенд — Django + Django REST Framework.
Данные обрабатываются через REST API и отображаются в интерактивном графе.

---

### 📋 Требования

- Установлен [Docker](https://www.docker.com/)
- Установлен [Docker Compose](https://docs.docker.com/compose/)

### 🛠 Запуск

1. Клонируйте репозиторий или распакуйте архив:

   ```bash
   git clone https://github.com/Chidorigafuchi/repos_dependency_graph.git
   cd repos_dependency_graph
   ```
2. Перед запуском необходимо создать .env файл в папке backend по примеру .env.example:

   ```env
   DJANGO_SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   REDIS_HOST=redis
   REDIS_PORT=6379
   REDIS_DB=0
   CELERY_BROKER_URL=redis://redis:6379/1
   CELERY_RESULT_BACKEND=redis://redis:6379/2
   ```
3. Постройте и запустите контейнеры:

   ```bash
   docker-compose up --build
   ```
При первом запуске автоматически проводятся миграции


## Эндпоинты

| Метод  | URL                             | Описание |
|:------:|---------------------------------|-------------------------------------------------------------------|
| GET    | `/api/available_repos/`                   | Получение списка доступных репозиториев           |
| GET    | `/api/package_info/?name=Имя`   | Получение информации о пакете по имени                  |
| GET    | `/api/tracked_packages_list/`   | Получение списка отслеживаемых пакетов для пользователя           |
| POST   | `/api/package/`                 | Получение графа зависимостей для пакета по выбранным репозиториям |
| POST   | `/api/track_package/`           | Добавление пакета в список отслеживаемых          |
| DELETE | `/api/tracked_packages_list/`   | Удаление пакета из списка отслеживаемых          |
---


## Пример POST-запросов

**POST** `/api/package/`

```json
{
  "name": "groonga",
  "repos": ["https://repo1.red-soft.ru/redos/8.0/x86_64/os/", "https://repo1.red-soft.ru/redos/8.0/x86_64/updates/"],
}
```
### Ответ
```json
{
  "package_package": {
        "groonga-libs": ["groonga", "groonga-plugin-suggest"],
        "groonga-plugin-suggest": ["groonga"],
        "libedit": ["groonga"],
        "groonga": ["groonga-server-common"],
        "groonga-server-common": ["groonga-server-gqtp", "groonga-httpd"]
    },
  "set_package": {
        "SET_glibc-langpack": ["glibc"],
        },
  "library_package": {
        "groonga": ["libgcc_s.so.1", "libgcc_s.so.1(GLIBC_2.0)"],
        "glibc": ["(glibc-gconv-extra(x86-32) = 2.36-3.red80 if redhat-rpm-config)"],
        "libedit": ["libtinfo.so.6"],
        },
  "sets": {
        "SET_glibc-langpack": ["glibc-langpack-ar", "glibc-langpack-kw"]
    }
}
```

**POST** `/api/track_package/`

```json
{
  "name": "groonga",
  "repos": ["https://repo1.red-soft.ru/redos/8.0/x86_64/os/"]
}
```
### Ответ
```json
{
  "track_created": "true"
}
```