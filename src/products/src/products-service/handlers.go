// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"

	"strconv"
)

var image_root_url = os.Getenv("IMAGE_ROOT_URL")

func FullyQualifyCategoryImageUrl(c Category) Category {
	log.Println("Fully qualifying category image URL")
	c.Image = image_root_url + c.Name + "/" + c.Image
	return c
}

func FullyQualifyCategoryImageUrls(categories Categories) Categories {
	log.Println("Fully qualifying category image URLs")
	ret := make([]Category, len(categories))

	for i, c := range categories {
		c.Image = image_root_url + c.Name + "/" + c.Image
		ret[i] = c
	}
	return ret
}

func FullyQualifyProductImageUrl(p Product) Product {
	log.Println("Fully qualifying product image URL")
	p.Image = image_root_url + p.Category + "/" + p.Image
	return p
}

func FullyQualifyProductImageUrls(products Products) Products {
	log.Println("Fully qualifying product image URLs")
	ret := make([]Product, len(products))

	for i, p := range products {
		p.Image = image_root_url + p.Category + "/" + p.Image
		ret[i] = p
	}
	return ret
}

// Index Handler
func Index(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "Welcome to the Products Web Service")
}

// ProductIndex Handler
func ProductIndex(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)

	ret := RepoFindALLProduct()

	fullyQualify, _ := strconv.ParseBool(r.URL.Query().Get("fullyQualifyImageUrls"))
	if fullyQualify {
		ret = FullyQualifyProductImageUrls(ret)
	}

	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

// CategoryIndex Handler
func CategoryIndex(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)

	ret := RepoFindALLCategories()

	fullyQualify, _ := strconv.ParseBool(r.URL.Query().Get("fullyQualifyImageUrls"))
	if fullyQualify {
		ret = FullyQualifyCategoryImageUrls(ret)
	}

	// TODO
	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

// ProductShow Handler
func ProductShow(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	vars := mux.Vars(r)

	ret := RepoFindProduct(vars["productID"])

	fullyQualify, _ := strconv.ParseBool(r.URL.Query().Get("fullyQualifyImageUrls"))
	if fullyQualify {
		ret = FullyQualifyProductImageUrl(ret)
	}

	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

// CategoryShow Handler
func CategoryShow(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	vars := mux.Vars(r)
	categoryName := vars["categoryName"]

	ret := RepoFindProductByCategory(categoryName)

	fullyQualify, _ := strconv.ParseBool(r.URL.Query().Get("fullyQualifyImageUrls"))
	if fullyQualify {
		ret = FullyQualifyProductImageUrls(ret)
	}

	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

// ProductFeatured Handler
func ProductFeatured(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	ret := RepoFindFeatured()

	fullyQualify, _ := strconv.ParseBool(r.URL.Query().Get("fullyQualifyImageUrls"))
	if fullyQualify {
		ret = FullyQualifyProductImageUrls(ret)
	}

	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

// enableCors
func enableCors(w *http.ResponseWriter) {
	(*w).Header().Set("Access-Control-Allow-Origin", "*")
}

// Update a Product for one item Handler
func UpdateProduct(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)
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
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(422) // unprocessable entity
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}

	log.Println("UpdateProducts  ", product)

	ret := RepoUpdateProduct(vars["productID"], product)

	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

// Update Stock Quantity for one item Handler
func UpdateInventory(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

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
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(422) // unprocessable entity
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}

	log.Println("UpdateInventory --> ", inventory)

	ret := RepoUpdateInventoryDelta(vars["productID"], inventory.StockDelta)

	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

// Create a new Product
func NewProduct(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	var product Product
	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 1048576))
	if err != nil {
		panic(err)
	}
	if err := r.Body.Close(); err != nil {
		panic(err)
	}
	if err := json.Unmarshal(body, &product); err != nil {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(422) // unprocessable entity
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}

	log.Println("NewProduct  ", product)

	ret := RepoNewProduct(product)

	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}
