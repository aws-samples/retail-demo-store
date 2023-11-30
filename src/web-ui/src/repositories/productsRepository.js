// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";
import resolveBaseURL from './resolveBaseURL'
import { Auth } from 'aws-amplify';

const baseURL = resolveBaseURL(
    import.meta.env.VITE_PRODUCTS_SERVICE_DOMAIN,
    import.meta.env.VITE_PRODUCTS_SERVICE_PORT,
    import.meta.env.VITE_PRODUCTS_SERVICE_PATH
)

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
    async getProduct(productID, user) {
        if (!productID || productID.length == 0)
            throw "productID required"
        if (Array.isArray(productID))
            productID = productID.join()

        let params = {}
        let headers = {}
        if (user) {
            params['user'] = user
            await Auth.currentSession()
                    .then((session) => session.idToken.jwtToken)
                    .then((idToken) => headers['Authorization'] = "Bearer " + idToken)
        } 
        return connection.get(`${resource}/id/${productID}`, { params: params, headers: headers })        
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