"use strict";

var allowedOrigin = process.env.ALLOWED_ORIGIN

exports.handler = async (event, context, callback) => {
  // Retrieve header parameters from the Lambda function input:
  var headers = event.headers;

  // Simple check to ensure Origin header matches the web-ui domain
  if (checkOriginHeader(headers)) {
    callback(null, generateAllow('me', event.methodArn));
  } else {
    console.log("Invalid Origin: " + headers.Origin);
    callback(null, generateDeny('me', event.methodArn));
  }
}
  
// Helper function to generate an IAM policy
var generatePolicy = function(principalId, effect, resource) {
 // Required output:
 var authResponse = {};
  authResponse.principalId = principalId;
 if (effect && resource) {
     var policyDocument = {};
      policyDocument.Version = '2012-10-17'; // default version
     policyDocument.Statement = [];
     var statementOne = {};
      statementOne.Action = 'execute-api:Invoke'; // default action
     statementOne.Effect = effect;
      statementOne.Resource = resource;
      policyDocument.Statement[0] = statementOne;
      authResponse.policyDocument = policyDocument;
  }
 
 return authResponse;
}
  
var generateAllow = function(principalId, resource) {
 return generatePolicy(principalId, 'Allow', resource);
}
  
var generateDeny = function(principalId, resource) {
 return generatePolicy(principalId, 'Deny', resource);
}

var checkOriginHeader = function(headers) {
  return headers.Origin == allowedOrigin;
}