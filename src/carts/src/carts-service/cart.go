// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

// Cart Struct
type Cart struct {
	ID       string    `json:"id" yaml:"id"`
	Username string    `json:"username" yaml:"username"`
	Items    CartItems `json:"items" yaml:"items"`
}

// Carts Array
type Carts []Cart

// CartItem Struct
type CartItem struct {
	ProductID string  `json:"product_id" yaml:"product_id"`
	Quantity  int     `json:"quantity" yaml:"quantity"`
	Price     float32 `json:"price" yaml:"price"`
}

// CartItems Array
type CartItems []CartItem
