// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import { get, post, put } from 'aws-amplify/api';

const resource = "/orders";
const apiName = 'demoServices';

export default {
    async get() {
        const restOperation = get({
            apiName: apiName,
            path: `${resource}/all`
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async getOrderByID(orderID) {
        if (!orderID || orderID.length == 0)
            throw "orderID required"
        const restOperation = get({
            apiName: apiName,
            path: `${resource}/id/${orderID}`
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async getOrdersByUsername(username) {
        if (!username || username.length == 0)
            throw "username required"
        const restOperation = get({
            apiName: apiName,
            path: `${resource}/username/${username}`
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async updateOrder(order) {
        if (!order)
            throw "order required"
        const restOperation = put({
            apiName: apiName,
            path: `${resource}/id/${order.id}`,
            options: {
                body: order
              }
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async createOrder(order) {
        if (!order)
            throw "order required"
        order.channel = 'WEB'
        order.channel_detail = {
            channel_id: 1,
            channel_geo: 'US'
        }
        delete order.ttl
        
        const restOperation = post({
            apiName: apiName,
            path: resource,
            options: {
                body: order
            }
        });
        const { body } = await restOperation.response;
        return body.json();
    },  
}