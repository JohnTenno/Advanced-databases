-- Read-only companion package for the blog web application.
-- Schema: HR (Oracle Database 21c XE, service XEPDB1)
--
-- blog_database.sql owns the model and blog_pkg, which holds the whole CRUD.
-- That file is never modified. What lives here is only the set of queries the
-- web interface needs and blog_pkg does not expose:
--
--   * reading which tags and categories an article already carries
--     (blog_pkg can assign and remove them, but not list them)
--   * catalogs filtered down to what is not assigned yet, for the pickers
--   * listings joining article + author + comment total, so a table does not
--     need one extra round trip per row
--
-- Every write still goes through blog_pkg. This package holds no INSERT,
-- UPDATE or DELETE at all: it only opens cursors.
--
-- Run AFTER blog_database.sql.

CREATE OR REPLACE PACKAGE blog_web_pkg AS

  -- Blog wide totals for the landing page.
  PROCEDURE dashboard(
    p_result OUT SYS_REFCURSOR
  );

  -- Articles with their author name and comment total.
  PROCEDURE list_articles_full(
    p_result OUT SYS_REFCURSOR
  );

  -- A single article with its author name and comment total.
  PROCEDURE get_article_full(
    p_article_id IN articles.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  );

  -- Tags already assigned to an article.
  PROCEDURE list_article_tags(
    p_article_id IN articles.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  );

  -- Categories already assigned to an article.
  PROCEDURE list_article_categories(
    p_article_id IN articles.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  );

  -- Tags the article does not carry yet (fills the assign picker).
  PROCEDURE list_available_tags(
    p_article_id IN articles.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  );

  -- Categories the article does not carry yet (fills the assign picker).
  PROCEDURE list_available_categories(
    p_article_id IN articles.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  );

  -- Tags along with how many articles use each one.
  PROCEDURE list_tags_with_usage(
    p_result OUT SYS_REFCURSOR
  );

  -- Categories along with how many articles use each one.
  PROCEDURE list_categories_with_usage(
    p_result OUT SYS_REFCURSOR
  );

  -- Users along with how much content they have authored.
  PROCEDURE list_users_with_usage(
    p_result OUT SYS_REFCURSOR
  );

END blog_web_pkg;
/

CREATE OR REPLACE PACKAGE BODY blog_web_pkg AS

  -- One row holding a counter per table in the model.
  PROCEDURE dashboard(
    p_result OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT (SELECT COUNT(*) FROM blog_users)  AS total_users,
             (SELECT COUNT(*) FROM articles)    AS total_articles,
             (SELECT COUNT(*) FROM articles
               WHERE status = 'PUBLISHED')      AS total_published,
             (SELECT COUNT(*) FROM articles
               WHERE status = 'DRAFT')          AS total_drafts,
             (SELECT COUNT(*) FROM comments)    AS total_comments,
             (SELECT COUNT(*) FROM tags)        AS total_tags,
             (SELECT COUNT(*) FROM categories)  AS total_categories
        FROM dual;
  END dashboard;

  -- The comment total comes from blog_pkg.count_article_comments so the
  -- main package's function is reused instead of repeating the COUNT.
  PROCEDURE list_articles_full(
    p_result OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT a.article_id,
             a.user_id,
             u.name AS author_name,
             a.title,
             a.post_date,
             a.status,
             blog_pkg.count_article_comments(a.article_id) AS comment_count
        FROM articles a
        JOIN blog_users u ON u.user_id = a.user_id
       ORDER BY a.post_date DESC, a.article_id DESC;
  END list_articles_full;

  -- Same as the listing but for one article, body text included.
  PROCEDURE get_article_full(
    p_article_id IN articles.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT a.article_id,
             a.user_id,
             u.name  AS author_name,
             u.email AS author_email,
             a.title,
             a.body_text,
             a.post_date,
             a.status,
             blog_pkg.count_article_comments(a.article_id) AS comment_count
        FROM articles a
        JOIN blog_users u ON u.user_id = a.user_id
       WHERE a.article_id = p_article_id;
  END get_article_full;

  -- Walks the article_tags bridge table to return the article's tags.
  PROCEDURE list_article_tags(
    p_article_id IN articles.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT t.tag_id, t.name, t.url
        FROM article_tags at
        JOIN tags t ON t.tag_id = at.tag_id
       WHERE at.article_id = p_article_id
       ORDER BY t.name;
  END list_article_tags;

  -- Same as tags, through the article_categories bridge table.
  PROCEDURE list_article_categories(
    p_article_id IN articles.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT c.category_id, c.name, c.url
        FROM article_categories ac
        JOIN categories c ON c.category_id = ac.category_id
       WHERE ac.article_id = p_article_id
       ORDER BY c.name;
  END list_article_categories;

  -- Catalog minus what is already assigned, so the picker never repeats one.
  PROCEDURE list_available_tags(
    p_article_id IN articles.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT t.tag_id, t.name, t.url
        FROM tags t
       WHERE NOT EXISTS (
               SELECT 1
                 FROM article_tags at
                WHERE at.tag_id = t.tag_id
                  AND at.article_id = p_article_id)
       ORDER BY t.name;
  END list_available_tags;

  PROCEDURE list_available_categories(
    p_article_id IN articles.article_id%TYPE,
    p_result     OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT c.category_id, c.name, c.url
        FROM categories c
       WHERE NOT EXISTS (
               SELECT 1
                 FROM article_categories ac
                WHERE ac.category_id = c.category_id
                  AND ac.article_id = p_article_id)
       ORDER BY c.name;
  END list_available_categories;

  -- LEFT JOIN so unused tags still show up, with a count of zero.
  PROCEDURE list_tags_with_usage(
    p_result OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT t.tag_id,
             t.name,
             t.url,
             COUNT(at.article_id) AS article_count
        FROM tags t
        LEFT JOIN article_tags at ON at.tag_id = t.tag_id
       GROUP BY t.tag_id, t.name, t.url
       ORDER BY t.name;
  END list_tags_with_usage;

  PROCEDURE list_categories_with_usage(
    p_result OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT c.category_id,
             c.name,
             c.url,
             COUNT(ac.article_id) AS article_count
        FROM categories c
        LEFT JOIN article_categories ac ON ac.category_id = c.category_id
       GROUP BY c.category_id, c.name, c.url
       ORDER BY c.name;
  END list_categories_with_usage;

  -- The counts are subqueries: two JOINs would multiply the rows against
  -- each other and inflate both totals.
  PROCEDURE list_users_with_usage(
    p_result OUT SYS_REFCURSOR
  ) IS
  BEGIN
    OPEN p_result FOR
      SELECT u.user_id,
             u.name,
             u.email,
             u.created_at,
             (SELECT COUNT(*) FROM articles a
               WHERE a.user_id = u.user_id) AS article_count,
             (SELECT COUNT(*) FROM comments c
               WHERE c.user_id = u.user_id) AS comment_count
        FROM blog_users u
       ORDER BY u.user_id;
  END list_users_with_usage;

END blog_web_pkg;
/
