// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";

const serviceDomain = process.env.VUE_APP_PRODUCTS_SERVICE_DOMAIN;
const servicePort = process.env.VUE_APP_PRODUCTS_SERVICE_PORT;
const baseURL = `${serviceDomain}:${servicePort}`;

const connection = axios.create({
    baseURL
})

const resource = "/products";
export default {
    get() {
        return connection.get(`${resource}/all`)
    },
    getFeatured() {
        return connection.get(`${resource}/featured`)
    },
    getProduct(productID) {
        if (!productID || productID.length == 0)
            throw "productID required"
        return connection.get(`${resource}/id/${productID}`)
    },
    getProductsByCategory(categoryName) {
        if (!categoryName || categoryName.length == 0)
            throw "categoryName required"
        return connection.get(`${resource}/category/${categoryName}`)
    },
    getCategories() {
        return connection.get(`categories/all`)
    }
}