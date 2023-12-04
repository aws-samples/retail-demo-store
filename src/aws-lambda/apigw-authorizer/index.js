"use strict";
const { CognitoJwtVerifier } = require("aws-jwt-verify");

const jwtVerifier = CognitoJwtVerifier.create({
  userPoolId: process.env.USER_POOL_ID,
  tokenUse: "id",
  clientId: process.env.CLIENT_ID,
});

function resolveAuthorizationHeader(authorizationHeader) {
  if (authorizationHeader.startsWith("Bearer ")){
    return authorizationHeader.substring(7, authorizationHeader.length);
  } else {
    throw "Authorization header value must match 'Bearer <token>'"
  }
}   

exports.handler = async (event) => {
  const authorizationHeader = event.headers.authorization;
  // At the moment we are just going to validate any presented token
  // In the future we will authorize specific routes based on the user   
  if (authorizationHeader) {
    try {
        const jwt = resolveAuthorizationHeader(authorizationHeader)
        await jwtVerifier.verify(jwt);
    } catch (err) {
        console.error("Access forbidden:", err);
        return {
            isAuthorized: false,
        };
    }
  }
  return {
    isAuthorized: true,
  };
};