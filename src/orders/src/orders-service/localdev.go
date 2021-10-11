// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/*
 * Supports developing locally where DDB is running locally using
 * amazon/dynamodb-local (Docker) or local DynamoDB.
 * https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html
 */

package main

import (
	"log"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/service/dynamodb"
)

func init() {
	if runningLocal {
		waitForLocalDDB()
		createOrdersTable()
	}
}

// waitForLocalDDB - since local DDB can take a couple seconds to startup, we give it some time.
func waitForLocalDDB() {
	log.Println("Verifying that local DynamoDB is running at: ", ddbEndpointOverride)

	ddbRunning := false

	for i := 0; i < 5; i++ {
		resp, _ := http.Get(ddbEndpointOverride)

		if resp != nil && resp.StatusCode >= 200 {
			log.Println("Received HTTP response from local DynamoDB service!")
			ddbRunning = true
			break
		}

		log.Println("Local DynamoDB service is not ready yet... pausing before trying again")
		time.Sleep(2 * time.Second)
	}

	if !ddbRunning {
		log.Panic("Local DynamoDB service not responding; verify that your docker-compose .env file is setup correctly")
	}
}

func createOrdersTable() error {
	log.Println("Creating orders table: ", ddbTableOrders)

	// Table definition mapped from /aws/cloudformation-templates/base/tables.yaml
	input := &dynamodb.CreateTableInput{
		AttributeDefinitions: []*dynamodb.AttributeDefinition{
			{
				AttributeName: aws.String("id"),
				AttributeType: aws.String("S"),
			},
			{
				AttributeName: aws.String("username"),
				AttributeType: aws.String("S"),
			},
		},
		KeySchema: []*dynamodb.KeySchemaElement{
			{
				AttributeName: aws.String("id"),
				KeyType:       aws.String("HASH"),
			},
		},
		BillingMode: aws.String("PAY_PER_REQUEST"),
		GlobalSecondaryIndexes: []*dynamodb.GlobalSecondaryIndex{
			{
				IndexName: aws.String("username-index"),
				KeySchema: []*dynamodb.KeySchemaElement{
					{
						AttributeName: aws.String("username"),
						KeyType:       aws.String("HASH"),
					},
				},
				Projection: &dynamodb.Projection{
					ProjectionType: aws.String("ALL"),
				},
			},
		},
		TableName: aws.String(ddbTableOrders),
	}

	_, err := dynamoClient.CreateTable(input)
	if err != nil {
		log.Println("Error creating orders table: ", ddbTableOrders)

		if aerr, ok := err.(awserr.Error); ok {
			if aerr.Code() == dynamodb.ErrCodeResourceInUseException {
				log.Println("Table already exists; continuing")
				err = nil
			} else {
				log.Println(err.Error())
			}
		} else {
			log.Println(err.Error())
		}
	}

	log.Println("Successfully created orders table")

	return err
}
