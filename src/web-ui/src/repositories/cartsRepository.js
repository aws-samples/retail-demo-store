// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";
import resolveBaseURL from './resolveBaseURL'

const baseURL = resolveBaseURL(
    process.env.VUE_APP_CARTS_SERVICE_DOMAIN,
    process.env.VUE_APP_CARTS_SERVICE_PORT,
    process.env.VUE_APP_CARTS_SERVICE_PATH
)

const connection = axios.create({
    baseURL
})

const resource = "/carts";
export default {
    get() {
        return connection.get(`${resource}/all`)
    },
    getCartByID(cartID) {
        if (!cartID || cartID.length == 0)
            throw "cartID required"
        return connection.get(`${resource}/id/${cartID}`)
    },    
    createCart(username) {
        if (!username || username.length == 0)
            throw "username required"
        let payload = {
            username: username  
        }
        return connection.post(`${resource}`, payload)
    },    
    updateCart(cart) {
        if (!cart)
            throw "cart required"
        return connection.put(`${resource}/id/${cart.id}`, cart)
    }
}