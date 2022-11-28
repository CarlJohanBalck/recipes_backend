package main

import (
	"database/sql"
	"fmt"

	_ "github.com/go-sql-driver/mysql"
	"github.com/tkanos/gonfig"
)

type Recipe struct {
	recipe_id         int
	recipe_name       string
	recipe_url        string
	recipe_helg       bool
	recipe_price      int
	recipe_image_url  string
	ingredient_id     int
	ingredient_name   string
	ingredient_amount string
	ingredient_unit   string

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
}

func main() {
	result := ingredients_for_recipe()
	fmt.Println("RESULT: ", result)
}

func GetConfig(params ...string) Recipe {
	conf := Recipe{}
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
		err = results.Scan(&recipe.recipe_name)
		s = append(s, recipe.recipe_name)
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
	// Create the database handle, confirm driver is present

	recipeList := "(12, 13)"
	s := make([]string, 3)
	db := connectDb()
	/* db, _ := sql.Open("mysql", conf.DB_USERNAME+":"+conf.DB_PASSWORD+"@tcp("+conf.DB_HOST+":"+conf.DB_PORT+")/"+conf.DB_NAME+"?parseTime=true") */
	defer db.Close()
	statement := conf.DB_QUERY_INGREDIENTS_1 + " " + recipeList + " " + conf.DB_QUERY_INGREDIENTS_2
	results, err := db.Query(statement)
	if err != nil {
		panic(err.Error())
	}
	for results.Next() {
		var recipe Recipe
		err = results.Scan(&recipe.ingredient_amount, &recipe.ingredient_unit, &recipe.ingredient_name)
		s = append(s, recipe.ingredient_amount, recipe.ingredient_unit, recipe.ingredient_name)
		if err != nil {
			panic(err.Error())
		}

	}
	return s
}
