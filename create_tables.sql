-- Creacion de tablas para la base de datos del blog.
-- Ejecutar despues de la limpieza inicial y antes de crear secuencias o paquetes.

CREATE TABLE blog_users (
  -- Tabla principal de usuarios/autores del blog.
  -- user_id es la llave primaria generada con seq_users.
  -- email se guarda como dato único y debe tener formato básico de correo.
  user_id    NUMBER(10)      NOT NULL,
  name       VARCHAR2(100)   NOT NULL,
  email      VARCHAR2(150)   NOT NULL,
  created_at DATE            DEFAULT SYSDATE NOT NULL,
  CONSTRAINT pk_blog_users PRIMARY KEY (user_id),
  CONSTRAINT uk_blog_users_email UNIQUE (email),
  CONSTRAINT ck_blog_users_email CHECK (email LIKE '%@%.%')
);

CREATE TABLE articles (
  -- Tabla de artículos escritos por los usuarios.
  -- Cada artículo pertenece a un usuario y se borra automáticamente si el usuario se elimina.
  -- status controla el estado editorial permitido: borrador, publicado o archivado.
  article_id NUMBER(10)      NOT NULL,
  user_id    NUMBER(10)      NOT NULL,
  title      VARCHAR2(200)   NOT NULL,
  body_text  CLOB            NOT NULL,
  post_date  DATE            DEFAULT SYSDATE NOT NULL,
  status     VARCHAR2(20)    DEFAULT 'DRAFT' NOT NULL,
  CONSTRAINT pk_articles PRIMARY KEY (article_id),
  CONSTRAINT fk_articles_user FOREIGN KEY (user_id)
    REFERENCES blog_users (user_id) ON DELETE CASCADE,
  CONSTRAINT ck_articles_status CHECK (status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED'))
);

CREATE TABLE comments (
  -- Tabla de comentarios publicados en los artículos.
  -- article_id obliga a que todo comentario pertenezca a un artículo existente.
  -- user_id es opcional: si el usuario se elimina, el comentario queda como anónimo.
  comment_id NUMBER(10)      NOT NULL,
  article_id NUMBER(10)      NOT NULL,
  user_id    NUMBER(10),
  name       VARCHAR2(100)   NOT NULL,
  url        VARCHAR2(250),
  body_text  VARCHAR2(1000)  NOT NULL,
  created_at DATE            DEFAULT SYSDATE NOT NULL,
  CONSTRAINT pk_comments PRIMARY KEY (comment_id),
  CONSTRAINT fk_comments_article FOREIGN KEY (article_id)
    REFERENCES articles (article_id) ON DELETE CASCADE,
  CONSTRAINT fk_comments_user FOREIGN KEY (user_id)
    REFERENCES blog_users (user_id) ON DELETE SET NULL
);

CREATE TABLE tags (
  -- Catálogo de etiquetas para clasificar artículos por tema.
  -- name y url son únicos para evitar etiquetas duplicadas o slugs repetidos.
  tag_id NUMBER(10)     NOT NULL,
  name   VARCHAR2(80)   NOT NULL,
  url    VARCHAR2(120)  NOT NULL,
  CONSTRAINT pk_tags PRIMARY KEY (tag_id),
  CONSTRAINT uk_tags_name UNIQUE (name),
  CONSTRAINT uk_tags_url UNIQUE (url)
);

CREATE TABLE categories (
  -- Catálogo de categorías principales del blog.
  -- name y url son únicos para mantener categorías identificables y enlazables.
  category_id NUMBER(10)     NOT NULL,
  name        VARCHAR2(80)   NOT NULL,
  url         VARCHAR2(120)  NOT NULL,
  CONSTRAINT pk_categories PRIMARY KEY (category_id),
  CONSTRAINT uk_categories_name UNIQUE (name),
  CONSTRAINT uk_categories_url UNIQUE (url)
);

CREATE TABLE article_tags (
  -- Tabla puente de relación muchos a muchos entre artículos y etiquetas.
  -- La llave primaria compuesta impide asignar la misma etiqueta dos veces al mismo artículo.
  article_id NUMBER(10) NOT NULL,
  tag_id     NUMBER(10) NOT NULL,
  CONSTRAINT pk_article_tags PRIMARY KEY (article_id, tag_id),
  CONSTRAINT fk_article_tags_article FOREIGN KEY (article_id)
    REFERENCES articles (article_id) ON DELETE CASCADE,
  CONSTRAINT fk_article_tags_tag FOREIGN KEY (tag_id)
    REFERENCES tags (tag_id) ON DELETE CASCADE
);

CREATE TABLE article_categories (
  -- Tabla puente de relación muchos a muchos entre artículos y categorías.
  -- Permite que un artículo tenga varias categorías y que una categoría tenga varios artículos.
  article_id   NUMBER(10) NOT NULL,
  category_id  NUMBER(10) NOT NULL,
  CONSTRAINT pk_article_categories PRIMARY KEY (article_id, category_id),
  CONSTRAINT fk_article_categories_article FOREIGN KEY (article_id)
    REFERENCES articles (article_id) ON DELETE CASCADE,
  CONSTRAINT fk_article_categories_category FOREIGN KEY (category_id)
    REFERENCES categories (category_id) ON DELETE CASCADE
);
