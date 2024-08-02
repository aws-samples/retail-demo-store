// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { get } from 'aws-amplify/api';

const apiName = 'demoServices';

export default {
    async get_store_location() {
        const restOperation = get({
            apiName: apiName,
            path: '/store_location'
        });
        const { body }  = await restOperation.response;
        return body.json();
    },
    async get_customer_route() {
        const restOperation = get({
            apiName: apiName,
            path: '/customer_route'
        });
        const { body }  = await restOperation.response;
        return body.json();
    }
}