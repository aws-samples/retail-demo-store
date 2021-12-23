// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"

	"strconv"
	"strings"
)

var imageRootURL = os.Getenv("IMAGE_ROOT_URL")
var missingImageFile = "product_image_coming_soon.png"

// initResponse
func initResponse(w *http.ResponseWriter) {
	(*w).Header().Set("Access-Control-Allow-Origin", "*")
	(*w).Header().Set("Content-Type", "application/json; charset=UTF-8")
}

func fullyQualifyImageURLs(r *http.Request) bool {
	param := r.URL.Query().Get("fullyQualifyImageUrls")
	if len(param) == 0 {
		param = "1"
	}

	fullyQualify, _ := strconv.ParseBool(param)
	return fullyQualify
}

// fullyQualifyCategoryImageURL - fully qualifies image URL for a category
func fullyQualifyCategoryImageURL(r *http.Request, c *Category) {
	if fullyQualifyImageURLs(r) {
		if len(c.Image) > 0 && c.Image != missingImageFile {
			c.Image = imageRootURL + c.Name + "/" + c.Image
		} else {
			c.Image = imageRootURL + missingImageFile
		}
	} else if len(c.Image) == 0 || c.Image == missingImageFile {
		c.Image = missingImageFile
	}
}

// fullyQualifyCategoryImageURLs - fully qualifies image URL for categories
func fullyQualifyCategoryImageURLs(r *http.Request, categories *Categories) {
	for i := range *categories {
		category := &((*categories)[i])
		fullyQualifyCategoryImageURL(r, category)
	}
}

// fullyQualifyProductImageURL - fully qualifies image URL for a product
func fullyQualifyProductImageURL(r *http.Request, p *Product) {
	if fullyQualifyImageURLs(r) {
		if len(p.Image) > 0 && p.Image != missingImageFile {
			p.Image = imageRootURL + p.Category + "/" + p.Image
		} else {
			p.Image = imageRootURL + missingImageFile
		}
	} else if len(p.Image) == 0 || p.Image == missingImageFile {
		p.Image = missingImageFile
	}
}

// fullyQualifyProductImageURLs - fully qualifies image URLs for all products
func fullyQualifyProductImageURLs(r *http.Request, products *Products) {
	for i := range *products {
		product := &((*products)[i])
		fullyQualifyProductImageURL(r, product)
	}
}

// Index Handler
func Index(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "Welcome to the Products Web Service")
}

// ProductIndex Handler
func ProductIndex(w http.ResponseWriter, r *http.Request) {
	initResponse(&w)

	ret := RepoFindALLProducts()

	fullyQualifyProductImageURLs(r, &ret)

	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

// CategoryIndex Handler
func CategoryIndex(w http.ResponseWriter, r *http.Request) {
	initResponse(&w)

	ret := RepoFindALLCategories()

	fullyQualifyCategoryImageURLs(r, &ret)

	// TODO
	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

// ProductShow Handler
func ProductShow(w http.ResponseWriter, r *http.Request) {
	initResponse(&w)

	vars := mux.Vars(r)

	productIds := strings.Split(vars["productIDs"], ",")

	if len(productIds) > MAX_BATCH_GET_ITEM {
		http.Error(w, fmt.Sprintf("Maximum number of product IDs per request is %d", MAX_BATCH_GET_ITEM), http.StatusUnprocessableEntity)
		return
	}

	if len(productIds) > 1 {
		ret := RepoFindMultipleProducts(productIds)

		fullyQualifyProductImageURLs(r, &ret)

		if err := json.NewEncoder(w).Encode(ret); err != nil {
			panic(err)
		}
	} else {
		ret := RepoFindProduct(productIds[0])

		if !ret.Initialized() {
			http.Error(w, "Product not found", http.StatusNotFound)
			return
		}

		fullyQualifyProductImageURL(r, &ret)

		if err := json.NewEncoder(w).Encode(ret); err != nil {
			panic(err)
		}
	}
}

// CategoryShow Handler
func CategoryShow(w http.ResponseWriter, r *http.Request) {
	initResponse(&w)

	vars := mux.Vars(r)

	ret := RepoFindCategory(vars["categoryID"])

	if !ret.Initialized() {
		http.Error(w, "Category not found", http.StatusNotFound)
		return
	}

	fullyQualifyCategoryImageURL(r, &ret)

	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

// ProductInCategory Handler
func ProductInCategory(w http.ResponseWriter, r *http.Request) {
	initResponse(&w)

	vars := mux.Vars(r)
	categoryName := vars["categoryName"]

	ret := RepoFindProductByCategory(categoryName)

	fullyQualifyProductImageURLs(r, &ret)

	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

// ProductFeatured Handler
func ProductFeatured(w http.ResponseWriter, r *http.Request) {
	initResponse(&w)

	ret := RepoFindFeatured()

	fullyQualifyProductImageURLs(r, &ret)

	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

func validateProduct(product *Product) error {
	if len(product.Name) == 0 {
		return errors.New("Product name is required")
	}

	if product.Price < 0 {
		return errors.New("Product price cannot be a negative value")
	}

	if product.CurrentStock < 0 {
		return errors.New("Product current stock cannot be a negative value")
	}

	if len(product.Category) > 0 {
		categories := RepoFindCategoriesByName(product.Category)
		if len(categories) == 0 {
			return errors.New("Invalid product category; does not exist")
		}
	}

	return nil
}

// UpdateProduct - updates a product
func UpdateProduct(w http.ResponseWriter, r *http.Request) {
	initResponse(&w)

	vars := mux.Vars(r)

	print(vars)
	var product Product

	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 1048576))
	if err != nil {
		panic(err)
	}
	if err := r.Body.Close(); err != nil {
		panic(err)
	}
	if err := json.Unmarshal(body, &product); err != nil {
		http.Error(w, "Invalid request payload", http.StatusUnprocessableEntity)
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}

	if err := validateProduct(&product); err != nil {
		http.Error(w, err.Error(), http.StatusUnprocessableEntity)
		return
	}

	existingProduct := RepoFindProduct(vars["productID"])
	if !existingProduct.Initialized() {
		// Existing product does not exist
		http.Error(w, "Product not found", http.StatusNotFound)
		return
	}

	if err := RepoUpdateProduct(&existingProduct, &product); err != nil {
		http.Error(w, "Internal error updating product", http.StatusInternalServerError)
		return
	}

	fullyQualifyProductImageURL(r, &product)

	if err := json.NewEncoder(w).Encode(product); err != nil {
		panic(err)
	}
}

// UpdateInventory - updates stock quantity for one item
func UpdateInventory(w http.ResponseWriter, r *http.Request) {
	initResponse(&w)

	vars := mux.Vars(r)

	var inventory Inventory

	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 1048576))
	if err != nil {
		panic(err)
	}
	if err := r.Body.Close(); err != nil {
		panic(err)
	}
	log.Println("UpdateInventory Body ", body)

	if err := json.Unmarshal(body, &inventory); err != nil {
		http.Error(w, "Invalid request payload", http.StatusUnprocessableEntity)
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}

	log.Println("UpdateInventory --> ", inventory)

	// Get the current product
	product := RepoFindProduct(vars["productID"])
	if !product.Initialized() {
		// Existing product does not exist
		http.Error(w, "Product not found", http.StatusNotFound)
		return
	}

	if err := RepoUpdateInventoryDelta(&product, inventory.StockDelta); err != nil {
		panic(err)
	}

	fullyQualifyProductImageURL(r, &product)

	if err := json.NewEncoder(w).Encode(product); err != nil {
		panic(err)
	}
}

// NewProduct  - creates a new Product
func NewProduct(w http.ResponseWriter, r *http.Request) {
	initResponse(&w)

	var product Product
	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 1048576))
	if err != nil {
		panic(err)
	}
	if err := r.Body.Close(); err != nil {
		panic(err)
	}
	if err := json.Unmarshal(body, &product); err != nil {
		http.Error(w, "Invalid request payload", http.StatusUnprocessableEntity)
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}

	log.Println("NewProduct  ", product)

	if err := validateProduct(&product); err != nil {
		http.Error(w, err.Error(), http.StatusUnprocessableEntity)
		return
	}

	if err := RepoNewProduct(&product); err != nil {
		http.Error(w, "Internal error creating product", http.StatusInternalServerError)
		return
	}

	fullyQualifyProductImageURL(r, &product)

	if err := json.NewEncoder(w).Encode(product); err != nil {
		panic(err)
	}
}

// DeleteProduct - deletes a single product
func DeleteProduct(w http.ResponseWriter, r *http.Request) {
	initResponse(&w)

	vars := mux.Vars(r)

	// Get the current product
	product := RepoFindProduct(vars["productID"])
	if !product.Initialized() {
		// Existing product does not exist
		http.Error(w, "Product not found", http.StatusNotFound)
		return
	}

	if err := RepoDeleteProduct(&product); err != nil {
		http.Error(w, "Internal error deleting product", http.StatusInternalServerError)
	}
}
