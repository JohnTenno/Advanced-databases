"""Demo content for screenshots and manual testing.

The rows are inserted by calling the same services the web app uses, so
seeding doubles as a check that the packages actually work.
"""
from app.modules.articles import service as articles_service
from app.modules.articles import taxonomy
from app.modules.articles.dto import SaveArticleDto
from app.modules.categories import service as categories_service
from app.modules.categories.dto import SaveCategoryDto
from app.modules.comments import service as comments_service
from app.modules.comments.dto import SaveCommentDto
from app.modules.tags import service as tags_service
from app.modules.tags.dto import SaveTagDto
from app.modules.users import service as users_service
from app.modules.users.dto import SaveUserDto

USERS = [
    ("Ana Torres", "ana.torres@correo.com"),
    ("Luis Moreno", "luis.moreno@correo.com"),
    ("Sofia Ramirez", "sofia.ramirez@correo.com"),
]

TAGS = [
    ("plsql", "plsql"),
    ("oracle", "oracle"),
    ("cursores", "cursores"),
    ("modelado", "modelado"),
    ("python", "python"),
]

CATEGORIES = [
    ("Tutoriales", "tutoriales"),
    ("Avanzado", "avanzado"),
    ("Noticias", "noticias"),
]

# Bodies keep their blank lines so the CLOB round trip is visible on screen.
ARTICLES = [
    {
        "author": 0,
        "title": "Que son los procedimientos almacenados",
        "status": "PUBLISHED",
        "tags": ["plsql", "oracle"],
        "categories": ["Tutoriales"],
        "body": (
            "Un procedimiento almacenado es un bloque de PL/SQL con nombre que "
            "vive dentro de la base de datos.\n\n"
            "La ventaja principal es que la logica queda del lado del servidor: "
            "la aplicacion solo manda el nombre del procedimiento y sus "
            "parametros, no la sentencia completa. Eso reduce el trafico de red, "
            "evita repetir la misma consulta en cada programa que use la base y "
            "cierra la puerta a la inyeccion de SQL.\n\n"
            "En este proyecto todas las altas, bajas y cambios del blog pasan "
            "por el paquete blog_pkg. La aplicacion en Python no escribe ni una "
            "sola sentencia SQL."
        ),
    },
    {
        "author": 1,
        "title": "Cursores de referencia para devolver consultas",
        "status": "PUBLISHED",
        "tags": ["plsql", "cursores"],
        "categories": ["Tutoriales", "Avanzado"],
        "body": (
            "Un procedimiento no puede devolver una tabla, pero si puede abrir "
            "un SYS_REFCURSOR y entregarlo en un parametro de salida.\n\n"
            "Del lado de Python se crea un cursor con connection.cursor() y se "
            "pasa como ultimo argumento de callproc. Al volver, ese cursor ya "
            "apunta al resultado y se recorre como cualquier otro.\n\n"
            "Es la forma de mantener las consultas dentro del paquete sin perder "
            "la posibilidad de leerlas desde la aplicacion."
        ),
    },
    {
        "author": 1,
        "title": "Integridad referencial: CASCADE contra SET NULL",
        "status": "DRAFT",
        "tags": ["oracle", "modelado"],
        "categories": ["Avanzado"],
        "body": (
            "Las llaves foraneas del blog usan dos comportamientos distintos a "
            "proposito.\n\n"
            "Los articulos llevan ON DELETE CASCADE: si se borra al autor, sus "
            "articulos desaparecen con el, porque un articulo sin autor no "
            "tiene sentido en este modelo.\n\n"
            "Los comentarios llevan ON DELETE SET NULL sobre el usuario: al "
            "borrar la cuenta el comentario se queda, pero pasa a ser anonimo. "
            "Asi no se rompen las conversaciones de los articulos."
        ),
    },
]

# (article index, user index or None for anonymous, name, url, body)
COMMENTS = [
    (0, 1, "Luis Moreno", None,
     "Muy claro el ejemplo, sobre todo la parte de los parametros de salida."),
    (0, None, "Visitante", "https://blog-invitado.example.com",
     "Llegue buscando como evitar inyeccion de SQL y esto me resolvio la duda."),
    (0, 2, "Sofia Ramirez", None,
     "Falta mencionar los paquetes: agrupar procedimientos ayuda bastante."),
    (1, 0, "Ana Torres", None,
     "El cursor de referencia era justo lo que no me salia. Gracias."),
]


def run() -> None:
    """Populate an empty schema. Must run inside a Flask app context."""
    print("\nSeeding demo content...")

    user_ids = [users_service.create(SaveUserDto(name, email))
                for name, email in USERS]
    print(f"  {len(user_ids)} users")

    tag_ids = {name: tags_service.create(SaveTagDto(name, url))
               for name, url in TAGS}
    print(f"  {len(tag_ids)} tags")

    category_ids = {name: categories_service.create(SaveCategoryDto(name, url))
                    for name, url in CATEGORIES}
    print(f"  {len(category_ids)} categories")

    article_ids = []
    for item in ARTICLES:
        article_id = articles_service.create(SaveArticleDto(
            user_id=user_ids[item["author"]],
            title=item["title"],
            body_text=item["body"],
            status=item["status"]))
        article_ids.append(article_id)

        for tag_name in item["tags"]:
            taxonomy.assign_tag(article_id, tag_ids[tag_name])
        for category_name in item["categories"]:
            taxonomy.assign_category(article_id, category_ids[category_name])
    print(f"  {len(article_ids)} articles with their tags and categories")

    for article_index, user_index, name, url, body in COMMENTS:
        comments_service.create(article_ids[article_index], SaveCommentDto(
            user_id=user_ids[user_index] if user_index is not None else None,
            name=name, url=url, body_text=body))
    print(f"  {len(COMMENTS)} comments")
