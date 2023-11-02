// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";
import resolveBaseURL from './resolveBaseURL'

const baseURL = resolveBaseURL(
    import.meta.env.VITE_ORDERS_SERVICE_DOMAIN,
    import.meta.env.VITE_ORDERS_SERVICE_PORT,
    import.meta.env.VITE_ORDERS_SERVICE_PATH
)

const connection = axios.create({
    baseURL
})

const resource = "/orders";
export default {
    get() {
        return connection.get(`${resource}/all`)
    },
    getOrderByID(orderID) {
        if (!orderID || orderID.length == 0)
            throw "orderID required"
        return connection.get(`${resource}/id/${orderID}`)
    },
    getOrdersByUsername(username) {
        if (!username || username.length == 0)
            throw "username required"
        return connection.get(`${resource}/username/${username}`)
    },
    updateOrder(order) {
        if (!order)
            throw "order required"
        return connection.put(`${resource}/id/${order.id}`, order)
    },
    createOrder(order) {
        if (!order)
            throw "order required"
        order.channel = 'WEB'
        order.channel_detail = {
            channel_id: 1,
            channel_geo: 'US'
        }
        delete order.ttl

        return connection.post(`${resource}`, order)
    },  
}