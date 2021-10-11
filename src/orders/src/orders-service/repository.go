// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"fmt"
	"log"
	"strings"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	"github.com/aws/aws-sdk-go/service/dynamodb/expression"
	guuuid "github.com/google/uuid"
)

var currentID int

var orders Orders = Orders{}

// Init
func init() {
}

// RepoFindOrderByID Function
func RepoFindOrderByID(id string) Order {
	var order Order

	log.Println("RepoFindOrder: ", id, ddbTableOrders)

	id = strings.ToLower(id)

	result, err := dynamoClient.GetItem(&dynamodb.GetItemInput{
		TableName: aws.String(ddbTableOrders),
		Key: map[string]*dynamodb.AttributeValue{
			"id": {
				S: aws.String(id),
			},
		},
	})

	if err != nil {
		log.Println("get item error " + string(err.Error()))
		return order
	}

	if result.Item != nil {
		err = dynamodbattribute.UnmarshalMap(result.Item, &order)

		if err != nil {
			panic(fmt.Sprintf("Failed to unmarshal Record, %v", err))
		}

		log.Println("RepoFindOrder returning: ", order.ID, order.Username)
	}

	return order
}

// RepoFindOrdersByUsername Function
func RepoFindOrdersByUsername(username string) Orders {
	log.Println("RepoFindOrdersByUsername: ", username)

	var f Orders

	keycond := expression.Key("username").Equal(expression.Value(username))
	proj := expression.NamesList(expression.Name("id"),
		expression.Name("username"),
		expression.Name("billing_address"),
		expression.Name("channel"),
		expression.Name("channel_detail"),
		expression.Name("collection_phone"),
		expression.Name("delivery_complete"),
		expression.Name("delivery_status"),
		expression.Name("delivery_type"),
		expression.Name("items"),
		expression.Name("shipping_address"),
		expression.Name("total"),
	)
	expr, err := expression.NewBuilder().WithKeyCondition(keycond).WithProjection(proj).Build()

	if err != nil {
		log.Println("Got error building expression:")
		log.Println(err.Error())
	}

	params := &dynamodb.QueryInput{
		ExpressionAttributeNames:  expr.Names(),
		ExpressionAttributeValues: expr.Values(),
		KeyConditionExpression:    expr.KeyCondition(),
		ProjectionExpression:      expr.Projection(),
		TableName:                 aws.String(ddbTableOrders),
		IndexName:                 aws.String("username-index"),
	}
	// Make the DynamoDB Query API call
	result, err := dynamoClient.Query(params)

	if err != nil {
		log.Println("Got error QUERY expression:")
		log.Println(err.Error())
	}

	log.Println("RepoFindOrdersByUsername / items found =  ", len(result.Items))

	for _, i := range result.Items {
		item := Order{}

		err = dynamodbattribute.UnmarshalMap(i, &item)

		if err != nil {
			log.Println("Got error unmarshalling:")
			log.Println(err.Error())
		}

		f = append(f, item)
	}

	if len(result.Items) == 0 {
		f = make([]Order, 0)
	}

	return f
}

func RepoUpdateOrder(existingOrder *Order, updatedOrder *Order) Order {
	log.Printf("UpdateOrder from %#v to %#v", existingOrder, updatedOrder)

	av, err := dynamodbattribute.MarshalMap(updatedOrder)

	if err != nil {
		fmt.Println("Got error calling dynamodbattribute MarshalMap:")
		fmt.Println(err.Error())
	}

	input := &dynamodb.PutItemInput{
		Item:      av,
		TableName: aws.String(ddbTableOrders),
	}

	_, err = dynamoClient.PutItem(input)
	if err != nil {
		fmt.Println("Got error calling PutItem:")
		fmt.Println(err.Error())
	}

	return *updatedOrder
}

// RepoCreateOrder Function
func RepoCreateOrder(order Order) Order {
	log.Printf("RepoNeworder --> %#v", order)

	order.ID = strings.ToLower(guuuid.New().String())
	av, err := dynamodbattribute.MarshalMap(order)

	if err != nil {
		fmt.Println("Got error calling dynamodbattribute MarshalMap:")
		fmt.Println(err.Error())
	}

	input := &dynamodb.PutItemInput{
		Item:      av,
		TableName: aws.String(ddbTableOrders),
	}

	_, err = dynamoClient.PutItem(input)
	if err != nil {
		fmt.Println("Got error calling PutItem:")
		fmt.Println(err.Error())
	}

	return order
}
