const AWS = require('aws-sdk');
const Client = require('@amazonpay/amazon-pay-api-sdk-nodejs');

const amazonPayPublicKeyId = process.env.AmazonPayPublicKeyId;
const amazonPaySecretArn = process.env.AmazonPayPrivateKeySecretArn;

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


exports.handler = async (event) => {
    console.log(event);
    console.log(process.env);

    const keyFromSm = await getPrivateKey()

    const lineSplit = keyFromSm.split(' ');
    let headFootLineCount = 0
    const key = lineSplit.reduce((acc, val) => {
        acc += val
        if (val.includes('-----')) {
            headFootLineCount ++
        }
        if (headFootLineCount !== 2) {
            acc += ' '
        } else {
            acc += '\n'
        }
        return acc
    }, '')

    const config = {
        publicKeyId: amazonPayPublicKeyId,
        privateKey: key,
        region: 'US',
        sandbox: true
    };
    const testPayClient = new Client.AmazonPayClient(config);
    const signature = testPayClient.generateButtonSignature(event);

    return {
        statusCode: 200,
        body: {
            Signature: signature,
            Payload: event
        },
    };
};