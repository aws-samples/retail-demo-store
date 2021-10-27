// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/*
 * Supports developing locally where DDB is running locally using
 * amazon/dynamodb-local (Docker) or local DynamoDB.
 * https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html
 */

package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	yaml "gopkg.in/yaml.v2"
)

func init() {
	if runningLocal {
		waitForLocalDDB()
		loadData()
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

func loadData() {
	err := createProductsTable()
	if err != nil {
		log.Panic("Unable to create products table.")
	}

	err = loadProducts("/bin/data/products.yaml")
	if err != nil {
		log.Panic("Unable to load products file.")
	}

	err = createCategoriesTable()
	if err != nil {
		log.Panic("Unable to create categories table.")
	}

	err = loadCategories("/bin/data/categories.yaml")
	if err != nil {
		log.Panic("Unable to load category file.")
	}

	log.Println("Successfully loaded product and category data into DDB")
}

func createProductsTable() error {
	log.Println("Creating products table: ", ddbTableProducts)

	// Table definition mapped from /aws/cloudformation-templates/base/tables.yaml
	input := &dynamodb.CreateTableInput{
		AttributeDefinitions: []*dynamodb.AttributeDefinition{
			{
				AttributeName: aws.String("id"),
				AttributeType: aws.String("S"),
			},
			{
				AttributeName: aws.String("category"),
				AttributeType: aws.String("S"),
			},
			{
				AttributeName: aws.String("featured"),
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
				IndexName: aws.String("category-index"),
				KeySchema: []*dynamodb.KeySchemaElement{
					{
						AttributeName: aws.String("category"),
						KeyType:       aws.String("HASH"),
					},
				},
				Projection: &dynamodb.Projection{
					ProjectionType: aws.String("ALL"),
				},
			},
			{
				IndexName: aws.String("featured-index"),
				KeySchema: []*dynamodb.KeySchemaElement{
					{
						AttributeName: aws.String("featured"),
						KeyType:       aws.String("HASH"),
					},
				},
				Projection: &dynamodb.Projection{
					ProjectionType: aws.String("ALL"),
				},
			},
		},
		TableName: aws.String(ddbTableProducts),
	}

	_, err := dynamoClient.CreateTable(input)
	if err != nil {
		log.Println("Error creating products table: ", ddbTableProducts)

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

	return err
}

func loadProducts(filename string) error {
	start := time.Now()

	log.Println("Loading products from file: ", filename)

	var r Products

	bytes, err := ioutil.ReadFile(filename)
	if err != nil {
		return err
	}

	err = yaml.Unmarshal(bytes, &r)
	if err != nil {
		return err
	}

	for _, item := range r {

		av, err := dynamodbattribute.MarshalMap(item)

		if err != nil {
			return err
		}

		input := &dynamodb.PutItemInput{
			Item:      av,
			TableName: aws.String(ddbTableProducts),
		}

		_, err = dynamoClient.PutItem(input)
		if err != nil {
			fmt.Println("Got error calling PutItem:")
			fmt.Println(err.Error())

		}

	}

	log.Println("Products loaded in ", time.Since(start))

	return nil
}

func createCategoriesTable() error {
	log.Println("Creating categories table: ", ddbTableCategories)

	// Table definition mapped from /aws/cloudformation-templates/base/tables.yaml
	input := &dynamodb.CreateTableInput{
		AttributeDefinitions: []*dynamodb.AttributeDefinition{
			{
				AttributeName: aws.String("id"),
				AttributeType: aws.String("S"),
			},
			{
				AttributeName: aws.String("name"),
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
				IndexName: aws.String("name-index"),
				KeySchema: []*dynamodb.KeySchemaElement{
					{
						AttributeName: aws.String("name"),
						KeyType:       aws.String("HASH"),
					},
				},
				Projection: &dynamodb.Projection{
					ProjectionType: aws.String("ALL"),
				},
			},
		},
		TableName: aws.String(ddbTableCategories),
	}

	_, err := dynamoClient.CreateTable(input)
	if err != nil {
		log.Println("Error creating categories table: ", ddbTableCategories)

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

	return err
}

func loadCategories(filename string) error {

	start := time.Now()

	log.Println("Loading categories from file: ", filename)

	var r Categories

	bytes, err := ioutil.ReadFile(filename)
	if err != nil {
		return err
	}

	err = yaml.Unmarshal(bytes, &r)
	if err != nil {
		return err
	}
	for _, item := range r {
		av, err := dynamodbattribute.MarshalMap(item)

		if err != nil {
			return err
		}

		input := &dynamodb.PutItemInput{
			Item:      av,
			TableName: aws.String(ddbTableCategories),
		}

		_, err = dynamoClient.PutItem(input)
		if err != nil {
			fmt.Println("Got error calling PutItem:")
			fmt.Println(err.Error())
		}
	}

	log.Println("Categories loaded in ", time.Since(start))

	return nil
}
