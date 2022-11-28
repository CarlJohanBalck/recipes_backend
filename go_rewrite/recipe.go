package main

import (
	"database/sql"
	"fmt"

	_ "github.com/go-sql-driver/mysql"
	"github.com/tkanos/gonfig"
)

type Recipe struct {
	recipe_id        int
	recipe_name      string
	recipe_url       string
	recipe_helg      bool
	recipe_price     int
	recipe_image_url string

	DB_USERNAME      string
	DB_PASSWORD      string
	DB_PORT          string
	DB_HOST          string
	DB_NAME          string
	DB_QUERY_GET_ALL string
}

func main() {
	result := getRecipes()
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
func recipes_for_ingredinets() []string {
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
