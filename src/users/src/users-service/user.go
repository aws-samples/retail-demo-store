// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"time"
)

// User Struct
type User struct {
	ID             string     `json:"id" yaml:"id"`
	Username       string     `json:"username" yaml:"username"`
	Email          string     `json:"email" yaml:"email"`
	FirstName      string     `json:"first_name" yaml:"first_name"`
	LastName       string     `json:"last_name" yaml:"last_name"`
	Addresses      Addresses  `json:"addresses" yaml:"addresses"`
	Age            int        `json:"age" yaml:"age"`
	Gender         string     `json:"gender" yaml:"gender"`
	Persona        string     `json:"persona" yaml:"persona"`
	SignUpDate     *time.Time `json:"sign_up_date,omitempty"`
	LastSignInDate *time.Time `json:"last_sign_in_date,omitempty"`
	IdentityId     string     `json:"identity_id,omitempty"`
}

// Users Array
type Users []User

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

// Addresses Struct
type Addresses []Address
