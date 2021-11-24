// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

// Product Struct
// using omitempty as a DynamoDB optimization to create indexes
// IMPORTANT: if you change the shape of this struct, be sure to update the retaildemostore-lambda-load-products Lambda too!
type Product struct {
	ID               string  `json:"id" yaml:"id"`
	URL              string  `json:"url" yaml:"url"`
	SK               string  `json:"sk" yaml:"sk"`
	Name             string  `json:"name" yaml:"name"`
	Category         string  `json:"category" yaml:"category"`
	Style            string  `json:"style" yaml:"style"`
	Description      string  `json:"description" yaml:"description"`
	Aliases        []string `json:"aliases" yaml:"aliases"` // keywords for use with e.g. Alexa
	Price            float32 `json:"price" yaml:"price"`
	Image            string  `json:"image" yaml:"image"`
	Featured         string  `json:"featured,omitempty" yaml:"featured,omitempty"`
	GenderAffinity   string  `json:"gender_affinity,omitempty" yaml:"gender_affinity,omitempty"`
	CurrentStock     int     `json:"current_stock" yaml:"current_stock"`
}

// Initialized - indicates if instance has been initialized or not
func (p *Product) Initialized() bool { return p != nil && len(p.ID) > 0 }

// Products Array
type Products []Product

// Inventory Struct
type Inventory struct {
	StockDelta int `json:"stock_delta" yaml:"stock_delta"`
}
