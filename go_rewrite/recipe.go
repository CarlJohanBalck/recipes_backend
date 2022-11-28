package main

import (
	"database/sql"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	_ "github.com/go-sql-driver/mysql"
	"github.com/tkanos/gonfig"
)

type Recipe struct {
	ID               string `json:"id"`
	Recipe_name      string `json:"recipe_name"`
	Recipe_url       string `json:"recipe_url"`
	Recipe_helg      bool   `json:"recipe_helg"`
	Recipe_price     int    `json:"recipe_price"`
	Recipe_image_url string `json:"recipe_image_url"`
}

type Ingredient struct {
	ID                string `json:"id"`
	Ingredient_name   string `json:"ingredient_name"`
	Ingredient_amount string `json:"ingredient_amount"`
	Ingredient_unit   string `json:"ingredient_unit"`
}

type DbConf struct {
	DB_USERNAME                                 string
	DB_PASSWORD                                 string
	DB_PORT                                     string
	DB_HOST                                     string
	DB_NAME                                     string
	DB_QUERY_GET_ALL                            string
	DB_QUERY_GET_DISH_LIST                      string
	DB_QUERY_INGREDIENTS_1                      string
	DB_QUERY_INGREDIENTS_2                      string
	DB_QUERY_GET_RECIPES_BASED_ON_INGREDIENTS_1 string
	DB_QUERY_GET_RECIPES_BASED_ON_INGREDIENTS_2 string
	DB_QUERY_GET_RECIPES_BASED_ON_INGREDIENTS_3 string
	SERVER_CONF                                 string
}

var recipes = []Recipe{
	{ID: "1", Recipe_name: "Pannkakor"},
}

// getAlbums responds with the list of all albums as JSON.
func getRecipesTest(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, recipes)
}

// posRecipes adds an recipe from JSON received in the request body.
func postRecipes(c *gin.Context) {
	var newRecipe Recipe

	// Call BindJSON to bind the received JSON to
	// newRecipe.
	fmt.Printf("c: %v\n", c)
	if err := c.BindJSON(&newRecipe); err != nil {
		return
	}

	// Add the new album to the slice.
	recipes = append(recipes, newRecipe)

	c.IndentedJSON(http.StatusCreated, newRecipe)
}

func main() {
	router := gin.Default()
	router.GET("/recipes", getRecipesTest)
	router.POST("/recipes", postRecipes)
	router.Run("192.168.0.4:8080")
}

func GetConfig(params ...string) DbConf {
	conf := DbConf{}
	env := "dev"
	if len(params) > 0 {
		env = params[0]
	}
	fileName := fmt.Sprintf("./%s_config.json", env)
	gonfig.GetConf(fileName, &conf)
	return conf
}

func getRecipes() []string {
	conf := GetConfig()
	// Create the database handle, confirm driver is present
	db, _ := sql.Open("mysql", conf.DB_USERNAME+":"+conf.DB_PASSWORD+"@tcp("+conf.DB_HOST+":"+conf.DB_PORT+")/"+conf.DB_NAME+"?parseTime=true")
	defer db.Close()
	s := make([]string, 3)

	// Connect to maria db and get all recipes names
	results, err := db.Query(conf.DB_QUERY_GET_ALL)
	if err != nil {
		panic(err.Error())
	}
	for results.Next() {
		var recipe Recipe
		err = results.Scan(&recipe.Recipe_name)
		s = append(s, recipe.Recipe_name)
		if err != nil {
			panic(err.Error())
		}
	}
	return s

}

func connectDb() *sql.DB {
	conf := GetConfig()
	// Create the database handle, confirm driver is present
	db, _ := sql.Open("mysql", conf.DB_USERNAME+":"+conf.DB_PASSWORD+"@tcp("+conf.DB_HOST+":"+conf.DB_PORT+")/"+conf.DB_NAME+"?parseTime=true")
	return db
}

func ingredients_for_recipe() []string {
	conf := GetConfig()
	recipeList := "(12, 13)"
	s := make([]string, 3)
	db := connectDb()
	defer db.Close()
	statement := conf.DB_QUERY_INGREDIENTS_1 + " " + recipeList + " " + conf.DB_QUERY_INGREDIENTS_2
	results, err := db.Query(statement)
	if err != nil {
		panic(err.Error())
	}
	for results.Next() {
		var ingredient Ingredient
		err = results.Scan(&ingredient.Ingredient_amount, &ingredient.Ingredient_unit, &ingredient.Ingredient_name)
		s = append(s, ingredient.Ingredient_amount, ingredient.Ingredient_unit, ingredient.Ingredient_name)
		if err != nil {
			panic(err.Error())
		}

	}
	return s
}
