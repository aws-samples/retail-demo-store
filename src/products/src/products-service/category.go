// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

// Category Struct
type Category struct {
	ID    string `json:"id" yaml:"id"`
	URL   string `json:"url" yaml:"url"`
	Name  string `json:"name" yaml:"name"`
	Image string `json:"image" yaml:"image"`
}

// Categories Array
type Categories []Category
