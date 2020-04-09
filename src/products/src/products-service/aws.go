// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"os"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/ssm"
)

//var sess *session.Session
var sess, err = session.NewSession(&aws.Config{})

// read DynamoDB tables env variable
var ddb_table_products = os.Getenv("DDB_TABLE_PRODUCTS")
var ddb_table_categories = os.Getenv("DDB_TABLE_CATEGORIES")

var dynamoclient = dynamodb.New(sess)
var ssm_client = ssm.New(sess)

// Connect Stuff
func init() {
	
}
