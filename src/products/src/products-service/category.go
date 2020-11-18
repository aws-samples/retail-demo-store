// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

// Category Struct
// IMPORTANT: if you change the shape of this struct, be sure to update the retaildemostore-lambda-load-products Lambda too!
type Category struct {
	ID    string `json:"id" yaml:"id"`
	URL   string `json:"url" yaml:"url"`
	Name  string `json:"name" yaml:"name"`
	Image string `json:"image" yaml:"image"`
}

// Initialized - indicates if instance has been initialized or not
func (c *Category) Initialized() bool { return c != nil && len(c.ID) > 0 }

// Categories Array
type Categories []Category
