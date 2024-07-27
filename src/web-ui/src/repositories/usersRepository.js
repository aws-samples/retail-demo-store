// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { get, post, put } from 'aws-amplify/api';

const resource = "/users";
const apiName = 'demoServices';

export default {
    async get(offset, count) {
        if (!offset) {
            offset = 0
        }
        if (!count) {
            count = 50
        }
        const restOperation = get({
            apiName: apiName,
            path: `${resource}/all`,
            options: {
                queryParams: {
                    offset: offset,
                    count: count
                }
            }
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async getUnclaimedUser({primaryInterest, ageRange}) {
        const restOperation = get({
            apiName: apiName,
            path: `${resource}/unclaimed`,
            options: {
                queryParams: {
                    primaryPersona: primaryInterest,
                    ageRange: ageRange
                }
            }
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async getRandomUser() {
        const restOperation = get({
            apiName: apiName,
            path: `${resource}/random`
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async getUserByID(userID) {
        if (!userID || userID.length == 0)
            throw "userID required"
        const restOperation = get({
            apiName: apiName,
            path: `${resource}/id/${userID}`
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async getUserByUsername(username) {
        if (!username || username.length == 0)
            throw "username required"
        const restOperation = get({
            apiName: apiName,
            path: `${resource}/username/${username}`
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async getUserByIdentityId(identityId) {
        if (!identityId || identityId.length == 0)
            throw "identityId required"
        const restOperation = get({
            apiName: apiName,
            path: `${resource}/identityid/${identityId}`
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async createUser(provisionalUserId, username, email, identityId) {
        if (!username || username.length == 0)
            throw "username required"
        let user = {
            id: provisionalUserId,
            username: username,
            email: email,
            identity_id: identityId
        }
        const restOperation = post({
            apiName: apiName,
            path: resource,
            options: {
              body: user
            }
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async updateUser(user) {
        if (!user)
            throw "user required"
        const restOperation = put({
            apiName: apiName,
            path: `${resource}/id/${user.id}`,
            options: {
              body: user
            }
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async claimUser(userId) {
        const restOperation = put({
            apiName: apiName,
            path: `${resource}/id/${userId}/claim`,
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async verifyAndUpdateUserPhoneNumber(userId, phoneNumber) {
        if (!userId || userId.length == 0)
            throw "userId required"
        let payload = {
            user_id: userId,
            phone_number: phoneNumber        
        }
        const restOperation = put({
            apiName: apiName,
            path: `${resource}/id/${userId}/verifyphone`,
            options: {
              body: payload
            }
        });
        const { body } = await restOperation.response;
        return body.json();
    }
}