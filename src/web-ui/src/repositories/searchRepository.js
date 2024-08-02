// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { get } from 'aws-amplify/api';

const resource = "/search/products";
const apiName = 'demoServices';

export default {
    async searchProducts(val, size = 10, offset = 0) {
        if (!val || val.length == 0)
            throw "val required"
        const restOperation = get({
            apiName: apiName,
            path: resource,
            options: {
                queryParams: {
                    searchTerm: val,
                    size: size,
                    offset: offset
                }
                }
        });
        const { body } = await restOperation.response;
        return body.json();
    },
}