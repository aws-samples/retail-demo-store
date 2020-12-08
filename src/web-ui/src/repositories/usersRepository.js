// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";

const serviceDomain = process.env.VUE_APP_USERS_SERVICE_DOMAIN;
const servicePort = process.env.VUE_APP_USERS_SERVICE_PORT;
const baseURL = `${serviceDomain}:${servicePort}`;

const connection = axios.create({
    baseURL
})

const resource = "/users";
export default {
    get(offset, count) {
        if (!offset) {
            offset = 0
        }
        if (!count) {
            count = 50
        }
        return connection.get(`${resource}/all?offset=${offset}&count=${count}`)
    },
    getUserByID(userID) {
        if (!userID || userID.length == 0)
            throw "userID required"
        return connection.get(`${resource}/id/${userID}`)
    },
    getUserByUsername(username) {
        if (!username || username.length == 0)
            throw "username required"
        return connection.get(`${resource}/username/${username}`)
    },
    getUserByIdentityId(identityId) {
        if (!identityId || identityId.length == 0)
            throw "identityId required"
        return connection.get(`${resource}/identityid/${identityId}`)
    },
    createUser(provisionalUserId, username, email, identityId) {
        if (!username || username.length == 0)
            throw "username required"
        let user = {
            id: provisionalUserId,
            username: username,
            email: email,
            identity_id: identityId
        }
        return connection.post(`${resource}`, user)
    },
    updateUser(user) {
        if (!user)
            throw "user required"
        return connection.put(`${resource}/id/${user.id}`, user)
    }
}