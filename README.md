# Blog on Oracle with PL/SQL and Python

First-term project for **Advanced Databases** (Bases de Datos Avanzadas),
Universidad Autónoma de Chihuahua.

A web application that administers a blog whose data lives in Oracle. The
application **never executes SQL**: every operation is a call to a stored
procedure or function written in PL/SQL.

Code, comments and routes are in English. The user-facing text is in Spanish,
since that is the language the application is presented in.

## Data model

| Table                 | Purpose                                             |
| --------------------- | --------------------------------------------------- |
| `blog_users`          | Blog authors (`name`, `email`)                      |
| `articles`            | Posts (`title`, `post_date`, `body_text` CLOB)      |
| `comments`            | Reader replies attached to an article               |
| `tags`                | Tag catalog                                         |
| `categories`          | Category catalog                                    |
| `article_tags`        | Bridge table, article ↔ tag                         |
| `article_categories`  | Bridge table, article ↔ category                    |

Relationships: `users` 1-to-N `articles`, `users` 1-to-N `comments`,
`articles` 1-to-N `comments`, `articles` N-to-N `tags` and N-to-N `categories`.

## Architecture

Organised by feature module in the NestJS style: each folder under
[app/modules/](app/modules/) owns everything about one entity and exposes a
Flask blueprint.

```
app/
├── config.py               Settings read from the environment
├── core/                   Cross cutting pieces
│   ├── database.py           Oracle connection, one per request
│   ├── oracle.py             The only place that calls the PL/SQL packages
│   ├── exceptions.py         AppError + ORA error translation
│   ├── request_parser.py     Form field reading and validation (like pipes)
│   └── presentation.py       Template filters and globals
├── modules/
│   ├── users/
│   │   ├── dto.py            UserDto, UserSummaryDto, SaveUserDto
│   │   ├── repository.py     Calls into blog_pkg / blog_web_pkg
│   │   ├── service.py        Use cases
│   │   └── controller.py     HTTP routes
│   ├── articles/             (+ taxonomy.py for the N-to-N links)
│   ├── comments/
│   ├── tags/
│   ├── categories/
│   └── dashboard/
├── templates/              Jinja2 + Bootstrap 5
└── static/css/app.css      The few things Bootstrap does not cover
```

Every module follows the same chain:

```
controller  ->  service  ->  repository  ->  core/oracle  ->  blog_pkg
   (HTTP)      (use case)   (one function        (callproc /
                             per program)          callfunc)
```

DTOs are frozen dataclasses with two entry points: `from_row()` builds one from
an Oracle result row, and `from_form()` builds one from the submitted form and
validates it. That keeps the validation next to the type it produces.

## Design

Bootstrap 5 with a custom theme in
[app/static/css/app.css](app/static/css/app.css).

The palette is sampled directly from the university crest
([app/static/img/uach-crest.png](app/static/img/uach-crest.png)) rather than
picked by eye:

| Colour | Hex       | Where it comes from   | Where it is used            |
| ------ | --------- | --------------------- | --------------------------- |
| Purple | `#8C2889` | The ring              | Accent colour and actions   |
| Yellow | `#F9ED25` | The lightning bolt    | Active icons, draft state   |
| Green  | `#23945D` | The shield            | Published state             |
| Blue   | `#6EBDE3` | The sky               | Informational tints         |
| Ink    | `#2D1F0F` | The wordmark          | Text colour                 |

The look follows macOS: a translucent sidebar using `backdrop-filter`, a
sticky frosted toolbar, generous corner radii, hairline borders, soft layered
shadows, compact controls, and Inter standing in for SF Pro, which is not
licensed for the web.

The crest doubles as the sidebar logo and the favicon.

## Requirements

- Python 3.12 or newer
- Docker Desktop, for the Oracle XE container
- No Oracle Instant Client needed: `python-oracledb` runs in *thin* mode
- Bootstrap 5 and Bootstrap Icons load from a CDN, so there is no build step

## Setup

### 1. Start Oracle XE

```powershell
docker start oracle-xe-hr
```

If the container does not exist yet:

```powershell
docker run -d --name oracle-xe-hr -p 1521:1521 `
  -e ORACLE_PASSWORD=oracle -e APP_USER=hr -e APP_USER_PASSWORD=hr `
  gvenzl/oracle-xe:21-slim
```

The first run takes a couple of minutes. To confirm it is ready:

```powershell
docker logs oracle-xe-hr --tail 5     # should print "DATABASE IS READY TO USE!"
```

### 2. Prepare the Python environment

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
```

`.env` ships with the container's credentials (`hr` / `hr` on
`localhost:1521/xepdb1`).

### 3. Create the schema and load demo data

```powershell
.venv\Scripts\python.exe -m scripts.setup_db
```

This runs both `.sql` scripts, verifies that the packages compiled without
errors, and inserts 3 users, 5 tags, 3 categories, 3 articles and 4 comments.
The demo rows are created **through the application's own services**, so
seeding doubles as a check that the packages work.

Flags: `--schema-only` and `--seed-only`.

### 4. Run the application

```powershell
.venv\Scripts\python.exe main.py
```

Open <http://127.0.0.1:5000>.

## Why there are two packages

`blog_pkg` (in [blog_database.sql](blog_database.sql)) holds the **entire
CRUD** and is the only thing that writes to the tables.

`blog_web_pkg` (in [blog_extras.sql](blog_extras.sql)) is **read only**. It
exists because the interface needs queries `blog_pkg` does not expose, above
all *which tags and categories an article already carries*: `blog_pkg` offers
`assign_tag` and `remove_tag`, but no way to read the relationship back.
Putting those `SELECT`s loose in Python would have broken the rule that the
application writes no SQL, so they live in a separate package instead.
`blog_database.sql` was never modified.

## Database objects and where they are used

### `blog_pkg` — functions

| Function                  | Returns        | Module         |
| ------------------------- | -------------- | -------------- |
| `create_user`             | `user_id`      | `users`        |
| `create_article`          | `article_id`   | `articles`     |
| `create_comment`          | `comment_id`   | `comments`     |
| `create_tag`              | `tag_id`       | `tags`         |
| `create_category`         | `category_id`  | `categories`   |
| `count_article_comments`  | a total        | `articles`     |

### `blog_pkg` — procedures

| Module                | Procedures                                                              |
| --------------------- | ----------------------------------------------------------------------- |
| `users`               | `get_user`, `list_users`, `update_user`, `delete_user`                  |
| `articles`            | `get_article`, `list_articles`, `update_article`, `publish_article`, `delete_article` |
| `comments`            | `get_comment`, `list_comments_by_article`, `update_comment`, `delete_comment` |
| `tags`                | `get_tag`, `list_tags`, `update_tag`, `delete_tag`                      |
| `categories`          | `get_category`, `list_categories`, `update_category`, `delete_category` |
| `articles/taxonomy`   | `assign_tag`, `remove_tag`, `assign_category`, `remove_category`        |

### `blog_web_pkg` — supporting queries

`dashboard`, `list_articles_full`, `get_article_full`, `list_article_tags`,
`list_article_categories`, `list_available_tags`, `list_available_categories`,
`list_tags_with_usage`, `list_categories_with_usage`, `list_users_with_usage`.

## Implementation notes

- **Reference cursors.** Query procedures return a `SYS_REFCURSOR`. Python
  creates a cursor with `connection.cursor()` and passes it as the last
  argument of `callproc`; on return it already points at the result set.
  `core/oracle.fetch_all` turns it into dictionaries keyed by
  `cursor.description`, and each module's DTO gives those rows a type.

- **Transactions.** The packages never `COMMIT`. Python owns the transaction:
  a successful operation is committed, and anything Oracle raises is rolled
  back before the user is told about it.

- **CLOB.** `articles.body_text` is a `CLOB`. Reading uses
  `oracledb.defaults.fetch_lobs = False` so the text arrives as a plain `str`;
  writing needs nothing special, since python-oracledb binds a `str` to a CLOB
  parameter without the 32767 character ceiling a `VARCHAR2` bind would impose.

- **Errors.** The package's `RAISE_APPLICATION_ERROR` calls (ORA-20001 through
  ORA-20013) and constraint violations are translated by
  `core/exceptions.translate` into sentences a reader can act on, and the
  `AppError` handler shows them as a Bootstrap alert on the same screen instead
  of a 500 page.

- **Referential integrity.** Deleting a user takes their articles with it
  (`ON DELETE CASCADE`) and leaves their comments anonymous
  (`ON DELETE SET NULL`). Deleting an article takes its comments and links.
  The confirmation dialog spells out how many rows are about to be lost.

- **Tags and categories share templates** (`templates/catalog/`) because they
  have the same columns and the same CRUD; each controller passes its own
  labels and endpoint names.
