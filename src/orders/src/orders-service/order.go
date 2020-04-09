// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

// Order Struct
type Order struct {
	ID              string    		`json:"id" yaml:"id"`
	Username        string     		`json:"username" yaml:"username"`
	Items           OrderItems 		`json:"items" yaml:"items"`
	Total           float32    		`json:"total" yaml:"total"`
	BillingAddress  Address    		`json:"billing_address" yaml:"billing_address"`
	ShippingAddress Address    		`json:"shipping_address" yaml:"shipping_address"`
	Channel			string	   		`json:"channel" yaml:"channel"`
	ChannelDetail   ChannelDetail	`json:"channel_detail" yaml:"channel_detail"`
}

// Orders Array
type Orders []Order

// OrderItem Struct
type OrderItem struct {
	ProductID string  `json:"product_id" yaml:"product_id"`
	Quantity  int     `json:"quantity" yaml:"quantity"`
	Price     float32 `json:"price" yaml:"price"`
}

// OrderItems Array
type OrderItems []OrderItem

// Address Struct
type Address struct {
	FirstName string `json:"first_name" yaml:"first_name"`
	LastName  string `json:"last_name" yaml:"last_name"`
	Address1  string `json:"address1" yaml:"address1"`
	Address2  string `json:"address2" yaml:"address2"`
	Country   string `json:"country" yaml:"country"`
	City      string `json:"city" yaml:"city"`
	State     string `json:"state" yaml:"state"`
	ZipCode   string `json:"zipcode" yaml:"zipcode"`
	Default   bool   `json:"default" yaml:"default"`
}

// ChannelDetail Struct
type ChannelDetail struct {
	ChannelId  int     `json:"channel_id" yaml:"channel_id"`
	ChnnelGeo  string  `json:"channel_geo" yaml:"channel_geo"`
}