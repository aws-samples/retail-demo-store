// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import "net/http"

// Route Struct
type Route struct {
	Name        string
	Method      string
	Pattern     string
	HandlerFunc http.HandlerFunc
}

// Routes Array
type Routes []Route

var routes = Routes{
	Route{
		"Index",
		"GET",
		"/",
		Index,
	},
	Route{
		"ProductIndex",
		"GET",
		"/products/all",
		ProductIndex,
	},
	Route{
		"CategoryIndex",
		"GET",
		"/categories/all",
		CategoryIndex,
	},
	Route{
		"ProductShow",
		"GET",
		"/products/id/{productID}",
		ProductShow,
	},
	Route{
		"ProductFeatured",
		"GET",
		"/products/featured",
		ProductFeatured,
	},
	Route{
		"CategoryShow",
		"GET",
		"/products/category/{categoryName}",
		CategoryShow,
	},
}
