// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"strconv"
)

var currentID int

var carts = map[string]Cart{}


// RepoFindCartByID Function
func RepoFindCartByID(id string) Cart {
	cart, ok := carts[id]
	if !ok {
		return Cart{}
	}
	return cart
}

// RepoUpdateCart Function
func RepoUpdateCart(id string, cart Cart) Cart {
	_, ok := carts[id]

	if !ok {
		// return empty Cart if not found
		return Cart{}
	}

	cart.ID = id
	carts[id] = cart

	return cart
}

// RepoCreateCart Function
func RepoCreateCart(t Cart) Cart {
	currentID++
	t.ID = strconv.Itoa(currentID)
	carts[t.ID] = t
	return t
}
