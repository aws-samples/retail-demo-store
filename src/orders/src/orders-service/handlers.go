// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"net/http"

	"github.com/gorilla/mux"
)

// Index Handler
func Index(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "Welcome to the Orders Web Service")
}

// OrderIndex Handler
func OrderIndex(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	orders := RepoFindALLOrders()

	if err := json.NewEncoder(w).Encode(orders); err != nil {
		panic(err)
	}
}

// OrderIndexByUsername Handler
func OrderIndexByUsername(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	vars := mux.Vars(r)
	username := vars["username"]

	if err := json.NewEncoder(w).Encode(RepoFindOrdersByUsername(username)); err != nil {
		panic(err)
	}
}

// OrderShowByID Handler
func OrderShowByID(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	vars := mux.Vars(r)
	orderID := vars["orderID"]

	if err := json.NewEncoder(w).Encode(RepoFindOrderByID(orderID)); err != nil {
		panic(err)
	}
}

//OrderUpdate Func
func OrderUpdate(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	if (*r).Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	var order Order
	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 1048576))
	if err != nil {
		panic(err)
	}
	if err := r.Body.Close(); err != nil {
		panic(err)
	}
	if err := json.Unmarshal(body, &order); err != nil {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(422) // unprocessable entity
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}

	// Get existing order
	vars := mux.Vars(r)
	orderID := vars["orderID"]
	existingOrder := RepoFindOrderByID(orderID)
	if !existingOrder.Initialized() {
		// Existing order does not exist
		http.Error(w, "Order not found", http.StatusNotFound)
		return
	}

	if len(order.ID) > 0 && order.ID != existingOrder.ID {
		// Do not allow ID to be changed
		http.Error(w, "Cannot modify order ID", http.StatusUnprocessableEntity)
		return
	}

	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusCreated)
	if err := json.NewEncoder(w).Encode(RepoUpdateOrder(&existingOrder, &order)); err != nil {
		http.Error(w, "Internal error updating product", http.StatusInternalServerError)
		return
	}
}

//OrderCreate Func
func OrderCreate(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	if (*r).Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	var order Order
	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 1048576))
	if err != nil {
		panic(err)
	}
	if err := r.Body.Close(); err != nil {
		panic(err)
	}
	if err := json.Unmarshal(body, &order); err != nil {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(422) // unprocessable entity
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}

	t := RepoCreateOrder(order)
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusCreated)
	if err := json.NewEncoder(w).Encode(t); err != nil {
		panic(err)
	}
}

// enableCors
func enableCors(w *http.ResponseWriter) {
	(*w).Header().Set("Access-Control-Allow-Origin", "*")
	(*w).Header().Set("Access-Control-Allow-Methods", "POST, PUT, GET, OPTIONS")
	(*w).Header().Set("Access-Control-Allow-Headers", "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")
}
