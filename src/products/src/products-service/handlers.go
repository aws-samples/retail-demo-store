// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"os"
	"log"
	"encoding/json"
	"fmt"
	"net/http"

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
	productID, err := strconv.Atoi(vars["productID"])

	if err != nil {
		panic(err)
	}

	ret := RepoFindProduct(productID)

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
