-- Base de datos para administrar un blog en Oracle con PL/SQL.
-- Ejecutar con un usuario que tenga permisos para crear tablas, secuencias y paquetes.

SET SERVEROUTPUT ON;

-- Limpieza opcional para poder volver a ejecutar el script durante pruebas.
-- Cada bloque intenta eliminar un objeto; si no existe, ignora el error esperado.
-- Esto permite ejecutar el script varias veces sin detenerse por tablas o secuencias ausentes.
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE article_tags CASCADE CONSTRAINTS';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE article_categories CASCADE CONSTRAINTS';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE comments CASCADE CONSTRAINTS';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE articles CASCADE CONSTRAINTS';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE tags CASCADE CONSTRAINTS';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE categories CASCADE CONSTRAINTS';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE blog_users CASCADE CONSTRAINTS';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE seq_users';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -2289 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE seq_articles';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -2289 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE seq_comments';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -2289 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE seq_tags';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -2289 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE seq_categories';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -2289 THEN RAISE; END IF;
END;
/

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

-- Secuencias usadas para generar identificadores numéricos incrementales.
-- NOCACHE evita reservar valores en memoria; es simple para pruebas y demos.
CREATE SEQUENCE seq_users START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_articles START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_comments START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_tags START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_categories START WITH 1 INCREMENT BY 1 NOCACHE;

-- Especificación del paquete: define la API pública para manejar el blog.
-- Aquí solo se declaran funciones y procedimientos; la lógica está en el cuerpo del paquete.
CREATE OR REPLACE PACKAGE blog_pkg AS
  -- Crea un usuario y devuelve el user_id generado.
  FUNCTION create_user(
    p_name  IN blog_users.name%TYPE,
    p_email IN blog_users.email%TYPE
  ) RETURN NUMBER;

  -- Crea un artículo asociado a un usuario y devuelve el article_id generado.
  FUNCTION create_article(
    p_user_id   IN articles.user_id%TYPE,
    p_title     IN articles.title%TYPE,
    p_body_text IN articles.body_text%TYPE,
    p_status    IN articles.status%TYPE DEFAULT 'DRAFT'
  ) RETURN NUMBER;

  -- Crea un comentario para un artículo y devuelve el comment_id generado.
  FUNCTION create_comment(
    p_article_id IN comments.article_id%TYPE,
    p_user_id    IN comments.user_id%TYPE,
    p_name       IN comments.name%TYPE,
    p_url        IN comments.url%TYPE,
    p_body_text  IN comments.body_text%TYPE
  ) RETURN NUMBER;

  -- Crea una etiqueta y devuelve el tag_id generado.
  FUNCTION create_tag(
    p_name IN tags.name%TYPE,
    p_url  IN tags.url%TYPE
  ) RETURN NUMBER;

  -- Crea una categoría y devuelve el category_id generado.
  FUNCTION create_category(
    p_name IN categories.name%TYPE,
    p_url  IN categories.url%TYPE
  ) RETURN NUMBER;

  -- Obtiene un usuario por su identificador usando un cursor de salida.
  PROCEDURE get_user(
    p_user_id IN blog_users.user_id%TYPE,
    p_result  OUT SYS_REFCURSOR
  );

  -- Lista todos los usuarios ordenados por identificador.
  PROCEDURE list_users(
    p_result OUT SYS_REFCURSOR
  );

  -- Actualiza nombre y correo de un usuario existente.
  PROCEDURE update_user(
    p_user_id IN blog_users.user_id%TYPE,
    p_name    IN blog_users.name%TYPE,
    p_email   IN blog_users.email%TYPE
  );

  -- Elimina un usuario; sus artículos se eliminan por ON DELETE CASCADE.
  PROCEDURE delete_user(
    p_user_id IN blog_users.user_id%TYPE
  );

  -- Obtiene un artículo específico por su identificador.
  PROCEDURE get_article(
    p_article_id IN articles.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  );

  -- Lista los artículos del blog del más reciente al más antiguo.
  PROCEDURE list_articles(
    p_result OUT SYS_REFCURSOR
  );

  -- Actualiza los datos principales de un artículo existente.
  PROCEDURE update_article(
    p_article_id IN articles.article_id%TYPE,
    p_user_id    IN articles.user_id%TYPE,
    p_title      IN articles.title%TYPE,
    p_body_text  IN articles.body_text%TYPE,
    p_status     IN articles.status%TYPE
  );

  -- Obtiene un comentario por su identificador.
  PROCEDURE get_comment(
    p_comment_id IN comments.comment_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  );

  -- Lista todos los comentarios de un artículo, primero los más recientes.
  PROCEDURE list_comments_by_article(
    p_article_id IN comments.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  );

  -- Actualiza los datos editables de un comentario.
  PROCEDURE update_comment(
    p_comment_id IN comments.comment_id%TYPE,
    p_user_id    IN comments.user_id%TYPE,
    p_name       IN comments.name%TYPE,
    p_url        IN comments.url%TYPE,
    p_body_text  IN comments.body_text%TYPE
  );

  -- Elimina un comentario por su identificador.
  PROCEDURE delete_comment(
    p_comment_id IN comments.comment_id%TYPE
  );

  -- Obtiene una etiqueta por su identificador.
  PROCEDURE get_tag(
    p_tag_id IN tags.tag_id%TYPE,
    p_result OUT SYS_REFCURSOR
  );

  -- Lista todas las etiquetas ordenadas alfabéticamente.
  PROCEDURE list_tags(
    p_result OUT SYS_REFCURSOR
  );

  -- Actualiza nombre y URL/slug de una etiqueta.
  PROCEDURE update_tag(
    p_tag_id IN tags.tag_id%TYPE,
    p_name   IN tags.name%TYPE,
    p_url    IN tags.url%TYPE
  );

  -- Elimina una etiqueta y sus relaciones con artículos.
  PROCEDURE delete_tag(
    p_tag_id IN tags.tag_id%TYPE
  );

  -- Obtiene una categoría por su identificador.
  PROCEDURE get_category(
    p_category_id IN categories.category_id%TYPE,
    p_result      OUT SYS_REFCURSOR
  );

  -- Lista todas las categorías ordenadas alfabéticamente.
  PROCEDURE list_categories(
    p_result OUT SYS_REFCURSOR
  );

  -- Actualiza nombre y URL/slug de una categoría.
  PROCEDURE update_category(
    p_category_id IN categories.category_id%TYPE,
    p_name        IN categories.name%TYPE,
    p_url         IN categories.url%TYPE
  );

  -- Elimina una categoría y sus relaciones con artículos.
  PROCEDURE delete_category(
    p_category_id IN categories.category_id%TYPE
  );

  -- Asigna una etiqueta a un artículo.
  PROCEDURE assign_tag(
    p_article_id IN article_tags.article_id%TYPE,
    p_tag_id     IN article_tags.tag_id%TYPE
  );

  -- Quita una etiqueta asignada a un artículo.
  PROCEDURE remove_tag(
    p_article_id IN article_tags.article_id%TYPE,
    p_tag_id     IN article_tags.tag_id%TYPE
  );

  -- Asigna una categoría a un artículo.
  PROCEDURE assign_category(
    p_article_id  IN article_categories.article_id%TYPE,
    p_category_id IN article_categories.category_id%TYPE
  );

  -- Quita una categoría asignada a un artículo.
  PROCEDURE remove_category(
    p_article_id  IN article_categories.article_id%TYPE,
    p_category_id IN article_categories.category_id%TYPE
  );

  -- Publica un artículo: cambia su estado y actualiza la fecha de publicación.
  PROCEDURE publish_article(
    p_article_id IN articles.article_id%TYPE
  );

  -- Elimina un artículo; sus comentarios y relaciones se eliminan por cascada.
  PROCEDURE delete_article(
    p_article_id IN articles.article_id%TYPE
  );

  -- Cuenta cuántos comentarios tiene un artículo.
  FUNCTION count_article_comments(
    p_article_id IN comments.article_id%TYPE
  ) RETURN NUMBER;
END blog_pkg;
/

CREATE OR REPLACE PACKAGE BODY blog_pkg AS
  -- Implementación de create_user:
  -- toma el siguiente valor de la secuencia, inserta el usuario y devuelve su ID.
  FUNCTION create_user(
    p_name  IN blog_users.name%TYPE,
    p_email IN blog_users.email%TYPE
  ) RETURN NUMBER IS
    v_user_id blog_users.user_id%TYPE;
  BEGIN
    v_user_id := seq_users.NEXTVAL;

    INSERT INTO blog_users (user_id, name, email)
    VALUES (v_user_id, p_name, LOWER(p_email));

    RETURN v_user_id;
  END create_user;

  -- Implementación de create_article:
  -- genera el ID, guarda el artículo y normaliza el estado a mayúsculas.
  FUNCTION create_article(
    p_user_id   IN articles.user_id%TYPE,
    p_title     IN articles.title%TYPE,
    p_body_text IN articles.body_text%TYPE,
    p_status    IN articles.status%TYPE DEFAULT 'DRAFT'
  ) RETURN NUMBER IS
    v_article_id articles.article_id%TYPE;
  BEGIN
    v_article_id := seq_articles.NEXTVAL;

    INSERT INTO articles (article_id, user_id, title, body_text, status)
    VALUES (v_article_id, p_user_id, p_title, p_body_text, UPPER(p_status));

    RETURN v_article_id;
  END create_article;

  -- Implementación de create_comment:
  -- crea un comentario asociado a un artículo y opcionalmente a un usuario.
  FUNCTION create_comment(
    p_article_id IN comments.article_id%TYPE,
    p_user_id    IN comments.user_id%TYPE,
    p_name       IN comments.name%TYPE,
    p_url        IN comments.url%TYPE,
    p_body_text  IN comments.body_text%TYPE
  ) RETURN NUMBER IS
    v_comment_id comments.comment_id%TYPE;
  BEGIN
    v_comment_id := seq_comments.NEXTVAL;

    INSERT INTO comments (comment_id, article_id, user_id, name, url, body_text)
    VALUES (v_comment_id, p_article_id, p_user_id, p_name, p_url, p_body_text);

    RETURN v_comment_id;
  END create_comment;

  -- Implementación de create_tag:
  -- registra una etiqueta reutilizable para clasificar artículos.
  FUNCTION create_tag(
    p_name IN tags.name%TYPE,
    p_url  IN tags.url%TYPE
  ) RETURN NUMBER IS
    v_tag_id tags.tag_id%TYPE;
  BEGIN
    v_tag_id := seq_tags.NEXTVAL;

    INSERT INTO tags (tag_id, name, url)
    VALUES (v_tag_id, p_name, p_url);

    RETURN v_tag_id;
  END create_tag;

  -- Implementación de create_category:
  -- registra una categoría reutilizable para agrupar artículos.
  FUNCTION create_category(
    p_name IN categories.name%TYPE,
    p_url  IN categories.url%TYPE
  ) RETURN NUMBER IS
    v_category_id categories.category_id%TYPE;
  BEGIN
    v_category_id := seq_categories.NEXTVAL;

    INSERT INTO categories (category_id, name, url)
    VALUES (v_category_id, p_name, p_url);

    RETURN v_category_id;
  END create_category;

  -- Abre un cursor con los datos de un solo usuario.
  PROCEDURE get_user(
    p_user_id IN blog_users.user_id%TYPE,
    p_result  OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT user_id, name, email, created_at
        FROM blog_users
       WHERE user_id = p_user_id;
  END get_user;

  -- Abre un cursor con todos los usuarios disponibles.
  PROCEDURE list_users(
    p_result OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT user_id, name, email, created_at
        FROM blog_users
       ORDER BY user_id;
  END list_users;

  -- Actualiza un usuario y valida que realmente exista mediante SQL%ROWCOUNT.
  PROCEDURE update_user(
    p_user_id IN blog_users.user_id%TYPE,
    p_name    IN blog_users.name%TYPE,
    p_email   IN blog_users.email%TYPE
  ) IS
  BEGIN
    UPDATE blog_users
       SET name = p_name,
           email = LOWER(p_email)
     WHERE user_id = p_user_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Si no se afectó ninguna fila, se informa un error de negocio.
      RAISE_APPLICATION_ERROR(-20003, 'El usuario no existe.');
    END IF;
  END update_user;

  -- Elimina un usuario; las llaves foráneas definen qué pasa con sus datos relacionados.
  PROCEDURE delete_user(
    p_user_id IN blog_users.user_id%TYPE
  ) IS
  BEGIN
    DELETE FROM blog_users
     WHERE user_id = p_user_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Evita que una eliminación inexistente parezca exitosa.
      RAISE_APPLICATION_ERROR(-20004, 'El usuario no existe.');
    END IF;
  END delete_user;

  -- Abre un cursor con los datos de un artículo específico.
  PROCEDURE get_article(
    p_article_id IN articles.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT article_id, user_id, title, body_text, post_date, status
        FROM articles
       WHERE article_id = p_article_id;
  END get_article;

  -- Abre un cursor con todos los artículos, ordenados por fecha descendente.
  PROCEDURE list_articles(
    p_result OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT article_id, user_id, title, body_text, post_date, status
        FROM articles
       ORDER BY post_date DESC, article_id DESC;
  END list_articles;

  -- Actualiza un artículo y normaliza el estado recibido.
  PROCEDURE update_article(
    p_article_id IN articles.article_id%TYPE,
    p_user_id    IN articles.user_id%TYPE,
    p_title      IN articles.title%TYPE,
    p_body_text  IN articles.body_text%TYPE,
    p_status     IN articles.status%TYPE
  ) IS
  BEGIN
    UPDATE articles
       SET user_id = p_user_id,
           title = p_title,
           body_text = p_body_text,
           status = UPPER(p_status)
     WHERE article_id = p_article_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Lanza error si el article_id no corresponde a ningún registro.
      RAISE_APPLICATION_ERROR(-20005, 'El articulo no existe.');
    END IF;
  END update_article;

  -- Abre un cursor con los datos de un comentario específico.
  PROCEDURE get_comment(
    p_comment_id IN comments.comment_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT comment_id, article_id, user_id, name, url, body_text, created_at
        FROM comments
       WHERE comment_id = p_comment_id;
  END get_comment;

  -- Abre un cursor con los comentarios de un artículo, primero los más nuevos.
  PROCEDURE list_comments_by_article(
    p_article_id IN comments.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT comment_id, article_id, user_id, name, url, body_text, created_at
        FROM comments
       WHERE article_id = p_article_id
       ORDER BY created_at DESC, comment_id DESC;
  END list_comments_by_article;

  -- Actualiza un comentario existente.
  PROCEDURE update_comment(
    p_comment_id IN comments.comment_id%TYPE,
    p_user_id    IN comments.user_id%TYPE,
    p_name       IN comments.name%TYPE,
    p_url        IN comments.url%TYPE,
    p_body_text  IN comments.body_text%TYPE
  ) IS
  BEGIN
    UPDATE comments
       SET user_id = p_user_id,
           name = p_name,
           url = p_url,
           body_text = p_body_text
     WHERE comment_id = p_comment_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Informa que no se encontró el comentario a modificar.
      RAISE_APPLICATION_ERROR(-20006, 'El comentario no existe.');
    END IF;
  END update_comment;

  -- Elimina un comentario por ID.
  PROCEDURE delete_comment(
    p_comment_id IN comments.comment_id%TYPE
  ) IS
  BEGIN
    DELETE FROM comments
     WHERE comment_id = p_comment_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Informa que no se encontró el comentario a eliminar.
      RAISE_APPLICATION_ERROR(-20007, 'El comentario no existe.');
    END IF;
  END delete_comment;

  -- Abre un cursor con una etiqueta específica.
  PROCEDURE get_tag(
    p_tag_id IN tags.tag_id%TYPE,
    p_result OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT tag_id, name, url
        FROM tags
       WHERE tag_id = p_tag_id;
  END get_tag;

  -- Abre un cursor con todas las etiquetas ordenadas por nombre.
  PROCEDURE list_tags(
    p_result OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT tag_id, name, url
        FROM tags
       ORDER BY name;
  END list_tags;

  -- Actualiza nombre y URL de una etiqueta.
  PROCEDURE update_tag(
    p_tag_id IN tags.tag_id%TYPE,
    p_name   IN tags.name%TYPE,
    p_url    IN tags.url%TYPE
  ) IS
  BEGIN
    UPDATE tags
       SET name = p_name,
           url = p_url
     WHERE tag_id = p_tag_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Informa que no se encontró la etiqueta a modificar.
      RAISE_APPLICATION_ERROR(-20008, 'La etiqueta no existe.');
    END IF;
  END update_tag;

  -- Elimina una etiqueta; article_tags se limpia por ON DELETE CASCADE.
  PROCEDURE delete_tag(
    p_tag_id IN tags.tag_id%TYPE
  ) IS
  BEGIN
    DELETE FROM tags
     WHERE tag_id = p_tag_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Informa que no se encontró la etiqueta a eliminar.
      RAISE_APPLICATION_ERROR(-20009, 'La etiqueta no existe.');
    END IF;
  END delete_tag;

  -- Abre un cursor con una categoría específica.
  PROCEDURE get_category(
    p_category_id IN categories.category_id%TYPE,
    p_result      OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT category_id, name, url
        FROM categories
       WHERE category_id = p_category_id;
  END get_category;

  -- Abre un cursor con todas las categorías ordenadas por nombre.
  PROCEDURE list_categories(
    p_result OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT category_id, name, url
        FROM categories
       ORDER BY name;
  END list_categories;

  -- Actualiza nombre y URL de una categoría.
  PROCEDURE update_category(
    p_category_id IN categories.category_id%TYPE,
    p_name        IN categories.name%TYPE,
    p_url         IN categories.url%TYPE
  ) IS
  BEGIN
    UPDATE categories
       SET name = p_name,
           url = p_url
     WHERE category_id = p_category_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Informa que no se encontró la categoría a modificar.
      RAISE_APPLICATION_ERROR(-20010, 'La categoria no existe.');
    END IF;
  END update_category;

  -- Elimina una categoría; article_categories se limpia por ON DELETE CASCADE.
  PROCEDURE delete_category(
    p_category_id IN categories.category_id%TYPE
  ) IS
  BEGIN
    DELETE FROM categories
     WHERE category_id = p_category_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Informa que no se encontró la categoría a eliminar.
      RAISE_APPLICATION_ERROR(-20011, 'La categoria no existe.');
    END IF;
  END delete_category;

  -- Inserta la relación artículo-etiqueta.
  -- Si ya existe, DUP_VAL_ON_INDEX se ignora para hacer la operación idempotente.
  PROCEDURE assign_tag(
    p_article_id IN article_tags.article_id%TYPE,
    p_tag_id     IN article_tags.tag_id%TYPE
  ) IS
  BEGIN
    INSERT INTO article_tags (article_id, tag_id)
    VALUES (p_article_id, p_tag_id);
  EXCEPTION
    WHEN DUP_VAL_ON_INDEX THEN
      NULL;
  END assign_tag;

  -- Elimina la relación artículo-etiqueta y valida que existiera.
  PROCEDURE remove_tag(
    p_article_id IN article_tags.article_id%TYPE,
    p_tag_id     IN article_tags.tag_id%TYPE
  ) IS
  BEGIN
    DELETE FROM article_tags
     WHERE article_id = p_article_id
       AND tag_id = p_tag_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Evita reportar éxito cuando la etiqueta no estaba asignada.
      RAISE_APPLICATION_ERROR(-20012, 'La etiqueta no esta asignada al articulo.');
    END IF;
  END remove_tag;

  -- Inserta la relación artículo-categoría.
  -- Si ya existe, DUP_VAL_ON_INDEX se ignora para evitar duplicados.
  PROCEDURE assign_category(
    p_article_id  IN article_categories.article_id%TYPE,
    p_category_id IN article_categories.category_id%TYPE
  ) IS
  BEGIN
    INSERT INTO article_categories (article_id, category_id)
    VALUES (p_article_id, p_category_id);
  EXCEPTION
    WHEN DUP_VAL_ON_INDEX THEN
      NULL;
  END assign_category;

  -- Elimina la relación artículo-categoría y valida que existiera.
  PROCEDURE remove_category(
    p_article_id  IN article_categories.article_id%TYPE,
    p_category_id IN article_categories.category_id%TYPE
  ) IS
  BEGIN
    DELETE FROM article_categories
     WHERE article_id = p_article_id
       AND category_id = p_category_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Evita reportar éxito cuando la categoría no estaba asignada.
      RAISE_APPLICATION_ERROR(-20013, 'La categoria no esta asignada al articulo.');
    END IF;
  END remove_category;

  -- Cambia un artículo a publicado y refresca la fecha de publicación.
  PROCEDURE publish_article(
    p_article_id IN articles.article_id%TYPE
  ) IS
  BEGIN
    UPDATE articles
       SET status = 'PUBLISHED',
           post_date = SYSDATE
     WHERE article_id = p_article_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Informa que no se encontró el artículo a publicar.
      RAISE_APPLICATION_ERROR(-20001, 'El articulo no existe.');
    END IF;
  END publish_article;

  -- Elimina un artículo; comentarios, etiquetas y categorías asociadas caen por cascada.
  PROCEDURE delete_article(
    p_article_id IN articles.article_id%TYPE
  ) IS
  BEGIN
    DELETE FROM articles
     WHERE article_id = p_article_id;

    IF SQL%ROWCOUNT = 0 THEN
      -- Informa que no se encontró el artículo a eliminar.
      RAISE_APPLICATION_ERROR(-20002, 'El articulo no existe.');
    END IF;
  END delete_article;

  -- Calcula el total de comentarios asociados a un artículo.
  FUNCTION count_article_comments(
    p_article_id IN comments.article_id%TYPE
  ) RETURN NUMBER IS
    v_total NUMBER;
  BEGIN
    SELECT COUNT(*)
      INTO v_total
      FROM comments
     WHERE article_id = p_article_id;

    RETURN v_total;
  END count_article_comments;
END blog_pkg;
/
