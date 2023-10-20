PORT = 5002
KEEP_EMAIL = "email"
KEEP_PASSWORD = "password"
DB_USER = "user"
DB_PASSWORD = "password"
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_DATABASE = "cool_db"
DB_QUERY_GET_ALL = "SELECT * FROM recipes_view"
DB_QUERY_GET_ALL_INGREDIENTS = "SELECT * FROM ingredient ORDER BY name"
DB_QUERY_GET_ALL_RECIPE_INGREDIENTS = "SELECT id FROM recipe_ingredient"
DB_QUERY_GET_ALL_UNITS = "SELECT * FROM unit"
DB_QUERY_GET_DISH_LIST = "SELECT r.name AS 'Name', r.url AS 'URL' FROM recipes_view r WHERE r.id in"
DB_QUERY_INGREDIENTS_1 = "SELECT cast(SUM(ri.amount) as VARCHAR(30)) AS 'Amount', un.name AS 'Unit of Measure', i.name AS 'Ingredient' FROM recipe r JOIN recipe_ingredient ri on r.id = ri.recipe_id JOIN ingredient i on i.id = ri.ingredient_id LEFT OUTER JOIN unit un on un.id = ri.unit_id WHERE r.id in"
DB_QUERY_INGREDIENTS_2 = "GROUP BY i.id ORDER BY i.category_id;"
DB_QUERY_GET_RECIPES_BASED_ON_INGREDIENTS_1 = "select name from recipe r where (select count(*) from ingredient i where i.id in"
DB_QUERY_GET_RECIPES_BASED_ON_INGREDIENTS_2 = ")= (select count(*) from recipe_ingredient ri inner join ingredient i on i.id = ri.ingredient_id where ri.recipe_id = r.id and i.id in"
DB_QUERY_GET_RECIPES_BASED_ON_INGREDIENTS_3 = " );"
DB_QUERY_ADD_RECIPE = "INSERT INTO recipe (id, name, url, helg, image_url, instructions) VALUES(%s,%s,%s,%s,%s,%s)"
DB_QUERY_ADD_INGREDIENT = "INSERT INTO recipe_ingredient (id, recipe_id, ingredient_id, unit_id, amount, price) VALUES(%s,%s,%s,%s,%s,0)"
DB_QUERY_ADD_RECIPE_INSTRUCTIONS_NULL = "INSERT INTO recipe (id, name, url, helg, image_url, instructions) VALUES(%s,%s,%s,%s,%s,NULL)"
DB_QUERY_ADD_RECIPE_URL_NULL = "INSERT INTO recipe (id, name, url, helg, image_url, instructions) VALUES(%s,%s,NULL,%s,%s,%s)"
DB_QUERY_MAX_ID_RECIPE="select MAX(id) from recipe"
DB_QUERY_MAX_ID_RECIPE_INGREDIENT="select MAX(id) from recipe_ingredient"
DB_QUERY_GET_INGREDIENT_ID="SELECT id from ingredient where scan_id= "

DB_QUERY_GET_PENTRY="select ingredient.id, ingredient.name, pentry_category.category, pentry_sub_category.sub_category from ingredient join pentry_category join pentry_sub_category where ingredient.id in (select ingredient_id from pentry) and ingredient.pentry_category=pentry_category.id and pentry_sub_category.id=ingredient.pentry_sub_category order by pentry_sub_category.id;"

DB_QUERY_GET_PENTRY_TO_ADD="select ingredient.id, ingredient.name, pentry_category.category from ingredient join pentry_category where ingredient.id in (select id from ingredient) and ingredient.pentry_category=pentry_category.id;"


DB_QUERY_GET_NEAR_READY_RECIPES="SELECT * FROM recipes_view r WHERE r.id in (select ri.recipe_id from recipe_ingredient as ri where ri.ingredient_id in (select ingredient_id from pentry) GROUP BY ri.recipe_id HAVING COUNT(*) >= 6);"


DB_QUERY_GET_DISH_LIST_REACT_NATIVE = "SELECT * FROM recipe r WHERE r.id in"
