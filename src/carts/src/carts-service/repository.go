// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"strconv"
)

var currentID int

var carts Carts = Carts{}

func init() {
}

// RepoFindCartByID Function
func RepoFindCartByID(id string) Cart {
	for _, t := range carts {
		if t.ID == id {
			return t
		}
	}
	// return empty Cart if not found
	return Cart{}
}

// RepoUpdateCart Function
func RepoUpdateCart(t Cart) Cart {

	for i := 0; i < len(carts); i++ {
		c := &carts[i]
		if c.ID == t.ID {
			c.Items = t.Items
			return RepoFindCartByID(t.ID)
		}
	}

	// return empty Cart if not found
	return Cart{}
}

// RepoCreateCart Function
func RepoCreateCart(t Cart) Cart {
	currentID++
	t.ID = strconv.Itoa(currentID)
	carts = append(carts, t)
	return RepoFindCartByID(t.ID)
}
