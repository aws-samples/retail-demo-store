// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

// Product Struct
// using omitempty as a DynamoDB optimization to create indexes
type Product struct {
	ID             string  `json:"id" yaml:"id"`
	URL            string  `json:"url" yaml:"url"`
	SK             string  `json:"sk" yaml:"sk"`
	Name           string  `json:"name" yaml:"name"`
	Category       string  `json:"category" yaml:"category"`
	Style          string  `json:"style" yaml:"style"`
	Description    string  `json:"description" yaml:"description"`
	Price          float32 `json:"price" yaml:"price"`
	Image          string  `json:"image" yaml:"image"`
	Featured       string  `json:"featured,omitempty" yaml:"featured,omitempty"`
	GenderAffinity string  `json:"gender_affinity,omitempty" yaml:"gender_affinity,omitempty"`
}

// Products Array
type Products []Product
