// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { get, post } from 'aws-amplify/api';

const resource = "/rooms";
const apiName = 'demoServices';

export default {
    async getRoom(roomId) {
      if (!roomId) {
          throw Error("user or roomId not defined")
      }
      const restOperation = get({
        apiName: apiName,
        path: `${resource}/${roomId}`
      });
      const { body } = await restOperation.response;
      return body.json();
    },
    async getRooms() {
      const restOperation = get({
        apiName: apiName,
        path: resource
      });
      const { body } = await restOperation.response;
      return body.json();
    },
    async createRoom(uploadKey, style) {

      const requestBody = {
          s3_key: uploadKey,
          style: style
      }
      console.log(requestBody)

      const restOperation = post({
        apiName: apiName,
        path: resource,
        options: {
          body: requestBody
        }
      });
      const { body, statusCode } = await restOperation.response;
      
      if (statusCode != 201) {
        throw new Error('Failed to generate room');
      }

      const data = await body.json();
      console.log('Generated room:', data);
      // Handle the response data (e.g., update UI)
      const roomId = data.room_generation_id;
      console.log(roomId)
      return roomId;
      }
      
}