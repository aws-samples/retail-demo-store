// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";

const serviceDomain = process.env.VUE_APP_CARTS_SERVICE_DOMAIN;
const servicePort = process.env.VUE_APP_CARTS_SERVICE_PORT;
const baseURL = `${serviceDomain}:${servicePort}`;

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