// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"strconv"
)

var currentID int

var orders Orders = Orders{}

// Init
func init() {
}

// RepoFindOrderByID Function
func RepoFindOrderByID(id string) Order {
	for _, t := range orders {
		if t.ID == id {
			return t
		}
	}
	// return empty Order if not found
	return Order{}
}

// RepoFindOrdersByUsername Function
func RepoFindOrdersByUsername(username string) Orders {

	var o Orders = Orders{}

	for _, t := range orders {
		if t.Username == username {
			o = append(o, t)
		}
	}

	return o
}

// RepoCreateOrder Function
func RepoCreateOrder(t Order) Order {
	currentID++
	t.ID = strconv.Itoa(currentID)
	orders = append(orders, t)
	return t
}
