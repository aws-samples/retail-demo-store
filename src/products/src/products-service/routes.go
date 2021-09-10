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
		"ProductShow",
		"GET",
		"/products/id/{productIDs}",
		ProductShow,
	},
	Route{
		"ProductFeatured",
		"GET",
		"/products/featured",
		ProductFeatured,
	},
	Route{
		"ProductInCategory",
		"GET",
		"/products/category/{categoryName}",
		ProductInCategory,
	},
	Route{
		"ProductUpdate",
		"PUT",
		"/products/id/{productID}",
		UpdateProduct,
	},
	Route{
		"ProductDelete",
		"DELETE",
		"/products/id/{productID}",
		DeleteProduct,
	},
	Route{
		"NewProduct",
		"POST",
		"/products",
		NewProduct,
	},
	Route{
		"InventoryUpdate",
		"PUT",
		"/products/id/{productID}/inventory",
		UpdateInventory,
	},
	Route{
		"CategoryIndex",
		"GET",
		"/categories/all",
		CategoryIndex,
	},
	Route{
		"CategoryShow",
		"GET",
		"/categories/id/{categoryID}",
		CategoryShow,
	},
}
