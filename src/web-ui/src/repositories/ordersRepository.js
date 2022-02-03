// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";

const serviceDomain = process.env.VUE_APP_ORDERS_SERVICE_DOMAIN;
const servicePort = process.env.VUE_APP_ORDERS_SERVICE_PORT;
const baseURL = `${serviceDomain}:${servicePort}`;

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
    getOrderByDeliveryStatus(deliveryStatus) {
        if (!deliveryStatus || deliveryStatus.length == 0)
            throw "deliveryStatus required"
        return connection.get(`${resource}/status/${deliveryStatus}`)
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
        order.channel_details = {
            channel_id: 1,
            channel_geo: 'US'
        }

        return connection.post(`${resource}`, order)
    },  
}