// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


import { get } from 'aws-amplify/api';

const resource = "/stream_details";
const apiName = 'demoServices';

export default {
    async get() {
        const restOperation = get({
            apiName: apiName,
            path: resource,        
        });
        const { body } = await restOperation.response;
        return body.json();
    },
}