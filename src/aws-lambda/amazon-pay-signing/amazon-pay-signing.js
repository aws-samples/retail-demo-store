// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

// Uses supplied secrets to Sign an Amazon Pay Payload - for example, for a checkout
// session config we sign a payload consisting of return URL, store ID, and charge permission type.
// This signed payload means Amazon Pay knows it was the merchant that setup the session,
// as it is signed with the private key that only the merchant should know.
// See https://developer.amazon.com/docs/amazon-pay-api-v2/signing-requests.html for more information.

const AWS = require('aws-sdk');
const Client = require('@amazonpay/amazon-pay-api-sdk-nodejs');

const amazonPayPublicKeyId = import.meta.env.AmazonPayPublicKeyId;
const amazonPaySecretArn = import.meta.env.AmazonPayPrivateKeySecretArn;

/**
 * Our Amazon Pay private key was saved in AWS Secrets Manager. Get it back.
 * @returns {Promise<String>}
 */
async function getPrivateKey () {
    let secretsManager = new AWS.SecretsManager();
    return new Promise((resolve,reject) => {
        secretsManager.getSecretValue({SecretId: amazonPaySecretArn}, function(err, data) {
            if (err) {
                reject(err);
            }
            else {
                resolve(data.SecretString);
            }
        });
    })
}

/**
 * Sign an Amazon Pay Payload - see details at the top of the file.
 * @param payload Event sent to Lambda
 * @returns {Promise<{body: {Signature: String, Payload: *}, statusCode: number}>}
 */
exports.handler = async (payload) => {
    console.log(payload);
    console.log(process.env);

    // Grab our Amazon Pay private key from Secrets Manager
    const keyFromSm = await getPrivateKey()

    // The key is a multi line file and would have been pasted into CloudFormation.
    // So we convert spaces back into new-lines, being careful that we do not add new
    // lines in the middle of the PEM start and end lines.
    const key = keyFromSm
                .replace(/ /g,'\n')
                .replace('-----BEGIN\nPRIVATE\nKEY-----',
                         '-----BEGIN PRIVATE KEY-----')
                .replace('-----END\nPRIVATE\nKEY-----',
                         '-----END PRIVATE KEY-----')

    // Set up your Amazon Pay SDK client with this secret.
    const config = {
        publicKeyId: amazonPayPublicKeyId,
        privateKey: key,
        region: 'US',
        sandbox: true
    };
    const testPayClient = new Client.AmazonPayClient(config);

    // The payload came to our Lambda as an event, we sign that.
    // It will be the same as what you send to the Lambda.
    const signature = testPayClient.generateButtonSignature(payload);

    return {
        statusCode: 200,
        body: {
            Signature: signature,
            Payload: payload
        },
    };
};