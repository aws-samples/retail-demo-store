// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	"github.com/aws/aws-sdk-go/service/dynamodb/expression"
	guuuid "github.com/google/uuid"
)

// Root/base URL to use when building fully-qualified URLs to product detail view.
var webRootURL = os.Getenv("WEB_ROOT_URL")

var MAX_BATCH_GET_ITEM = 100

func setProductURL(p *Product) {
	if len(webRootURL) > 0 {
		p.URL = webRootURL + "/#/product/" + p.ID
	}
}

func setCategoryURL(c *Category) {
	if len(webRootURL) > 0 && len(c.Name) > 0 {
		c.URL = webRootURL + "/#/category/" + c.Name
	}
}

// RepoFindProduct Function
func RepoFindProduct(id string) Product {
	var product Product

	id = strings.ToLower(id)

	log.Println("RepoFindProduct: ", id, ddbTableProducts)

	result, err := dynamoClient.GetItem(&dynamodb.GetItemInput{
		TableName: aws.String(ddbTableProducts),
		Key: map[string]*dynamodb.AttributeValue{
			"id": {
				S: aws.String(id),
			},
		},
	})

	if err != nil {
		log.Println("get item error " + string(err.Error()))
		return product
	}

	if result.Item != nil {
		err = dynamodbattribute.UnmarshalMap(result.Item, &product)

		if err != nil {
			panic(fmt.Sprintf("Failed to unmarshal Record, %v", err))
		}

		setProductURL(&product)

		log.Println("RepoFindProduct returning: ", product.Name, product.Category)
	}

	return product
}

// RepoFindMultipleProducts Function
func RepoFindMultipleProducts(ids []string) Products {
	if len(ids) > MAX_BATCH_GET_ITEM {
		panic(fmt.Sprintf("Failed to unmarshal Record, %d", MAX_BATCH_GET_ITEM))
	}

	var products Products

	mapOfAttrKeys := []map[string]*dynamodb.AttributeValue{}

	for _, id := range ids {
		mapOfAttrKeys = append(mapOfAttrKeys, map[string]*dynamodb.AttributeValue{
			"id": &dynamodb.AttributeValue{
				S: aws.String(id),
			},
		})
	}

	input := &dynamodb.BatchGetItemInput{
		RequestItems: map[string]*dynamodb.KeysAndAttributes{
			ddbTableProducts: &dynamodb.KeysAndAttributes{
				Keys: mapOfAttrKeys,
			},
		},
	}

	result, err := dynamoClient.BatchGetItem(input)

	if err != nil {
		log.Println("BatchGetItem error " + string(err.Error()))
		return products
	}

	var itemCount = 0

	for _, table := range result.Responses {
		for _, item := range table {
			product := Product{}

			err = dynamodbattribute.UnmarshalMap(item, &product)

			if err != nil {
				log.Println("Got error unmarshalling:")
				log.Println(err.Error())
			} else {
				setProductURL(&product)
			}

			products = append(products, product)
			itemCount += 1
		}
	}

	if itemCount == 0 {
		products = make([]Product, 0)
	}

	return products
}

// RepoFindCategory Function
func RepoFindCategory(id string) Category {
	var category Category

	id = strings.ToLower(id)

	log.Println("RepoFindCategory: ", id, ddbTableCategories)

	result, err := dynamoClient.GetItem(&dynamodb.GetItemInput{
		TableName: aws.String(ddbTableCategories),
		Key: map[string]*dynamodb.AttributeValue{
			"id": {
				S: aws.String(id),
			},
		},
	})

	if err != nil {
		log.Println("get item error " + string(err.Error()))
		return category
	}

	if result.Item != nil {
		err = dynamodbattribute.UnmarshalMap(result.Item, &category)

		if err != nil {
			panic(fmt.Sprintf("Failed to unmarshal Record, %v", err))
		}

		setCategoryURL(&category)

		log.Println("RepoFindCategory returning: ", category.Name)
	}

	return category
}

// RepoFindCategoriesByName Function
func RepoFindCategoriesByName(name string) Categories {
	var categories Categories

	log.Println("RepoFindCategoriesByName: ", name, ddbTableCategories)

	keycond := expression.Key("name").Equal(expression.Value(name))
	proj := expression.NamesList(expression.Name("id"),
		expression.Name("name"),
		expression.Name("image"))
	expr, err := expression.NewBuilder().WithKeyCondition(keycond).WithProjection(proj).Build()

	if err != nil {
		log.Println("Got error building expression:")
		log.Println(err.Error())
	}

	// Build the query input parameters
	params := &dynamodb.QueryInput{
		ExpressionAttributeNames:  expr.Names(),
		ExpressionAttributeValues: expr.Values(),
		KeyConditionExpression:    expr.KeyCondition(),
		ProjectionExpression:      expr.Projection(),
		TableName:                 aws.String(ddbTableCategories),
		IndexName:                 aws.String("name-index"),
	}
	// Make the DynamoDB Query API call
	result, err := dynamoClient.Query(params)

	if err != nil {
		log.Println("Got error QUERY expression:")
		log.Println(err.Error())
	}

	log.Println("RepoFindCategoriesByName / items found =  ", len(result.Items))

	for _, i := range result.Items {
		item := Category{}

		err = dynamodbattribute.UnmarshalMap(i, &item)

		if err != nil {
			log.Println("Got error unmarshalling:")
			log.Println(err.Error())
		} else {
			setCategoryURL(&item)
		}

		categories = append(categories, item)
	}

	if len(result.Items) == 0 {
		categories = make([]Category, 0)
	}

	return categories
}

// RepoFindProductByCategory Function
func RepoFindProductByCategory(category string) Products {

	log.Println("RepoFindProductByCategory: ", category)

	var f Products

	keycond := expression.Key("category").Equal(expression.Value(category))
	proj := expression.NamesList(expression.Name("id"),
		expression.Name("category"),
		expression.Name("name"),
		expression.Name("image"),
		expression.Name("style"),
		expression.Name("description"),
		expression.Name("price"),
		expression.Name("gender_affinity"),
		expression.Name("current_stock"))
	expr, err := expression.NewBuilder().WithKeyCondition(keycond).WithProjection(proj).Build()

	if err != nil {
		log.Println("Got error building expression:")
		log.Println(err.Error())
	}

	// Build the query input parameters
	params := &dynamodb.QueryInput{
		ExpressionAttributeNames:  expr.Names(),
		ExpressionAttributeValues: expr.Values(),
		KeyConditionExpression:    expr.KeyCondition(),
		ProjectionExpression:      expr.Projection(),
		TableName:                 aws.String(ddbTableProducts),
		IndexName:                 aws.String("category-index"),
	}
	// Make the DynamoDB Query API call
	result, err := dynamoClient.Query(params)

	if err != nil {
		log.Println("Got error QUERY expression:")
		log.Println(err.Error())
	}

	log.Println("RepoFindProductByCategory / items found =  ", len(result.Items))

	for _, i := range result.Items {
		item := Product{}

		err = dynamodbattribute.UnmarshalMap(i, &item)

		if err != nil {
			log.Println("Got error unmarshalling:")
			log.Println(err.Error())
		} else {
			setProductURL(&item)
		}

		f = append(f, item)
	}

	if len(result.Items) == 0 {
		f = make([]Product, 0)
	}

	return f
}

// RepoFindFeatured Function
func RepoFindFeatured() Products {

	log.Println("RepoFindFeatured | featured=true")

	var f Products

	filt := expression.Name("featured").Equal(expression.Value("true"))
	expr, err := expression.NewBuilder().WithFilter(filt).Build()

	if err != nil {
		log.Println("Got error building expression:")
		log.Println(err.Error())
	}

	// Build the query input
	// using index for performance (few items are featured)
	params := &dynamodb.ScanInput{
		ExpressionAttributeNames:  expr.Names(),
		ExpressionAttributeValues: expr.Values(),
		FilterExpression:          expr.Filter(),
		ProjectionExpression:      expr.Projection(),
		TableName:                 aws.String(ddbTableProducts),
		IndexName:                 aws.String("featured-index"),
	}
	// Make the DynamoDB Query API call
	result, err := dynamoClient.Scan(params)

	if err != nil {
		log.Println("Got error scan expression:")
		log.Println(err.Error())
	}

	log.Println("RepoFindProductFeatured / items found =  ", len(result.Items))

	for _, i := range result.Items {
		item := Product{}

		err = dynamodbattribute.UnmarshalMap(i, &item)

		if err != nil {
			log.Println("Got error unmarshalling:")
			log.Println(err.Error())
		} else {
			setProductURL(&item)
		}

		f = append(f, item)
	}

	if len(result.Items) == 0 {
		f = make([]Product, 0)
	}

	return f
}

// RepoFindALLCategories - loads all categories
func RepoFindALLCategories() Categories {
	// TODO: implement some caching

	log.Println("RepoFindALLCategories: ")

	var f Categories

	// Build the query input parameters
	params := &dynamodb.ScanInput{
		TableName: aws.String(ddbTableCategories),
	}
	// Make the DynamoDB Query API call
	result, err := dynamoClient.Scan(params)

	if err != nil {
		log.Println("Got error scan expression:")
		log.Println(err.Error())
	}

	log.Println("RepoFindALLCategories / items found =  ", len(result.Items))

	for _, i := range result.Items {
		item := Category{}

		err = dynamodbattribute.UnmarshalMap(i, &item)

		if err != nil {
			log.Println("Got error unmarshalling:")
			log.Println(err.Error())
		} else {
			setCategoryURL(&item)
		}

		f = append(f, item)
	}

	if len(result.Items) == 0 {
		f = make([]Category, 0)
	}

	return f
}

// RepoFindALLProducts Function
func RepoFindALLProducts() Products {

	log.Println("RepoFindALLProducts")

	var f Products

	// Build the query input parameters
	params := &dynamodb.ScanInput{
		TableName: aws.String(ddbTableProducts),
	}
	// Make the DynamoDB Query API call
	result, err := dynamoClient.Scan(params)

	if err != nil {
		log.Println("Got error scan expression:")
		log.Println(err.Error())
	}

	log.Println("RepoFindALLProducts / items found =  ", len(result.Items))

	for _, i := range result.Items {
		item := Product{}

		err = dynamodbattribute.UnmarshalMap(i, &item)

		if err != nil {
			log.Println("Got error unmarshalling:")
			log.Println(err.Error())
		} else {
			setProductURL(&item)
		}

		f = append(f, item)
	}

	if len(result.Items) == 0 {
		f = make([]Product, 0)
	}

	return f
}

// RepoUpdateProduct - updates an existing product
func RepoUpdateProduct(existingProduct *Product, updatedProduct *Product) error {
	updatedProduct.ID = existingProduct.ID // Ensure we're not changing product ID.
	updatedProduct.URL = ""                // URL is generated so ignore if specified
	log.Printf("UpdateProduct from %#v to %#v", existingProduct, updatedProduct)

	av, err := dynamodbattribute.MarshalMap(updatedProduct)

	if err != nil {
		fmt.Println("Got error calling dynamodbattribute MarshalMap:")
		fmt.Println(err.Error())
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

	setProductURL(updatedProduct)

	return err
}

// RepoUpdateInventoryDelta - updates a product's current inventory
func RepoUpdateInventoryDelta(product *Product, stockDelta int) error {

	log.Printf("RepoUpdateInventoryDelta for product %#v, delta: %v", product, stockDelta)

	if product.CurrentStock+stockDelta < 0 {
		// ensuring we don't get negative stocks, just down to zero stock
		// FUTURE: allow backorders via negative current stock?
		stockDelta = -product.CurrentStock
	}

	input := &dynamodb.UpdateItemInput{
		ExpressionAttributeValues: map[string]*dynamodb.AttributeValue{
			":stock_delta": {
				N: aws.String(strconv.Itoa(stockDelta)),
			},
			":currstock": {
				N: aws.String(strconv.Itoa(product.CurrentStock)),
			},
		},
		TableName: aws.String(ddbTableProducts),
		Key: map[string]*dynamodb.AttributeValue{
			"id": {
				S: aws.String(product.ID),
			},
			"category": {
				S: aws.String(product.Category),
			},
		},
		ReturnValues:        aws.String("UPDATED_NEW"),
		UpdateExpression:    aws.String("set current_stock = current_stock + :stock_delta"),
		ConditionExpression: aws.String("current_stock = :currstock"),
	}

	_, err = dynamoClient.UpdateItem(input)
	if err != nil {
		fmt.Println("Got error calling UpdateItem:")
		fmt.Println(err.Error())
	} else {
		product.CurrentStock = product.CurrentStock + stockDelta
	}

	return err
}

// RepoNewProduct - initializes and persists new product
func RepoNewProduct(product *Product) error {
	log.Printf("RepoNewProduct --> %#v", product)

	product.ID = strings.ToLower(guuuid.New().String())
	av, err := dynamodbattribute.MarshalMap(product)

	if err != nil {
		fmt.Println("Got error calling dynamodbattribute MarshalMap:")
		fmt.Println(err.Error())
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

	setProductURL(product)

	return err
}

// RepoDeleteProduct - deletes a single product
func RepoDeleteProduct(product *Product) error {
	log.Println("Deleting product: ", product)

	input := &dynamodb.DeleteItemInput{
		Key: map[string]*dynamodb.AttributeValue{
			"id": {
				S: aws.String(product.ID),
			},
			"category": {
				S: aws.String(product.Category),
			},
		},
		TableName: aws.String(ddbTableProducts),
	}

	_, err := dynamoClient.DeleteItem(input)

	if err != nil {
		fmt.Println("Got error calling DeleteItem:")
		fmt.Println(err.Error())
	}

	return err
}
