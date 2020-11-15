// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"log"
	"os"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
)

var sess, err = session.NewSession(&aws.Config{})

// DynamoDB table names passed via environment
var ddbTableProducts = os.Getenv("DDB_TABLE_PRODUCTS")
var ddbTableCategories = os.Getenv("DDB_TABLE_CATEGORIES")

// Allow DDB endpoint to be overridden to support amazon/dynamodb-local
var ddbEndpointOverride = os.Getenv("DDB_ENDPOINT_OVERRIDE")
var runningLocal bool

var dynamoClient *dynamodb.DynamoDB

// Initialize clients
func init() {
	if len(ddbEndpointOverride) > 0 {
		runningLocal = true
		log.Println("Creating DDB client with endpoint override: ", ddbEndpointOverride)
		creds := credentials.NewStaticCredentials("does", "not", "matter")
		awsConfig := &aws.Config{
			Credentials: creds,
			Region:      aws.String("us-east-1"),
			Endpoint:    aws.String(ddbEndpointOverride),
		}
		dynamoClient = dynamodb.New(sess, awsConfig)
	} else {
		runningLocal = false
		dynamoClient = dynamodb.New(sess)
	}
}
