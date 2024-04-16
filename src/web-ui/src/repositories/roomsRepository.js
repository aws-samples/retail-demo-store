// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";
import resolveBaseURL from './resolveBaseURL'
import { Auth } from 'aws-amplify';


const baseURL = resolveBaseURL(
    import.meta.env.VITE_PRODUCTS_SERVICE_DOMAIN,
    import.meta.env.VITE_PRODUCTS_SERVICE_PORT,
    import.meta.env.VITE_PRODUCTS_SERVICE_PATH
)

const connection = axios.create({
    baseURL
})

const resource = "rooms";
export default {
    async getRoom(roomId) {
        let headers = {}
        if (!roomId) {
            throw Error("user or roomId not defined")
        }
        await Auth.currentSession()
                .then((session) => session.idToken.jwtToken)
                .then((idToken) => headers['Authorization'] = "Bearer " + idToken)
        const response = await connection.get(`${resource}/${roomId}`, { headers: headers })    
        return response.data     
    },
    async getRooms() {
        let headers = {}
        await Auth.currentSession()
                .then((session) => session.idToken.jwtToken)
                .then((idToken) => headers['Authorization'] = "Bearer " + idToken)
        const response = await connection.get(`${resource}`, { headers: headers }) 
        return response.data
    },
    async createRoom(uploadKey, style) {
        const session = await Auth.currentSession(); // Fetch the current session
        const idToken = session.getIdToken().getJwtToken(); // Get the ID token

        console.log(uploadKey)
        const credentials= await Auth.currentCredentials();
        

        const requestBody = {
            s3_key: `private/${credentials.identityId}/${uploadKey}`,
            style: style
        }
        console.log(requestBody)

        const response = await fetch(`${baseURL}rooms`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${idToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        });
        if (!response.ok) {
          throw new Error('Failed to generate room');
        }

        const data = await response.json();
        console.log('Generated room:', data);
        // Handle the response data (e.g., update UI)
        const roomId = data.room_generation_id;
        console.log(roomId)
        return roomId;
      }
      
}