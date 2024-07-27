// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { get, post, put } from 'aws-amplify/api';

const resource = "/carts";
const apiName = 'demoServices';

export default {
    async get() {
        const restOperation = get({
            apiName: apiName,
            path: resource
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async getCartByID(cartID) {
        if (!cartID || cartID.length == 0)
            throw "cartID required"
        const restOperation = get({
            apiName: apiName,
            path: `${resource}/${cartID}`
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async getCartByUsername(username) {
        if (!username || username.length == 0)
            throw "username required"
        const restOperation = get({
            apiName: apiName,
            path: resource,
            options: {
                queryParams: {
                    username: username
                }
              }
        });
        const { body } = await restOperation.response;
        return body.json();
    },    
    async createCart(username) {

        if (!username || username.length == 0)
            throw "username required"
        let payload = {
            username: username  
        }
        const restOperation = post({
            apiName: apiName,
            path: resource,
            options: {
              body: payload
            }
          });
          const { body } = await restOperation.response;
          return body.json();
    },    
    async updateCart(cart) {
        if (!cart)
            throw "cart required"
        const restOperation = put({
            apiName: apiName,
            path: `${resource}/${cart.id}`,
            options: {
              body: cart
            }
          });
          const { body } = await restOperation.response;
          return body.json();
    },
    async signAmazonPayPayload(payload) {
        const restOperation = post({
            apiName: apiName,
            path: '/sign',
            options: {
              body: payload
            }
          });
          const { body } = await restOperation.response;
          return body.json();
    }
}