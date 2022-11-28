package main

import (
	"database/sql"
	"fmt"

	_ "github.com/go-sql-driver/mysql"
)

type Recipe struct {
	ID         int    `json:"id"`
	Recipename string `json:"recipename"`
}

func main() {
	result := getRecipes()
	fmt.Println("RESULT: ", result)

}

func getRecipes() []string {
	// Create the database handle, confirm driver is present
	db, _ := sql.Open("mysql", "root:root@tcp(localhost:3306)/cool_db?parseTime=true")
	defer db.Close()
	s := make([]string, 3)

	// Connect and check the server version
	results, err := db.Query("SELECT id, name FROM recipe")
	if err != nil {
		panic(err.Error())
	}
	for results.Next() {
		var recipe Recipe
		err = results.Scan(&recipe.ID, &recipe.Recipename)
		s = append(s, recipe.Recipename)
		if err != nil {
			panic(err.Error())
		}
		/* fmt.Println(recipe.Recipename) */
	}
	return s

}
