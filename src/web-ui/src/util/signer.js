import { toHex } from '@smithy/util-hex-encoding';
import { Sha256 } from '@aws-crypto/sha256-js';

// query params
const AMZ_DATE_QUERY_PARAM = 'X-Amz-Date';
const TOKEN_QUERY_PARAM = 'X-Amz-Security-Token';
const ALGORITHM_QUERY_PARAM = 'X-Amz-Algorithm';
const CREDENTIAL_QUERY_PARAM = 'X-Amz-Credential';
const SIGNED_HEADERS_QUERY_PARAM = 'X-Amz-SignedHeaders';
const EXPIRES_QUERY_PARAM = 'X-Amz-Expires';
const SIGNATURE_QUERY_PARAM = 'X-Amz-Signature';
// headers
const AUTH_HEADER = 'authorization';
const HOST_HEADER = 'host';
const AMZ_DATE_HEADER = AMZ_DATE_QUERY_PARAM.toLowerCase();
const TOKEN_HEADER = TOKEN_QUERY_PARAM.toLowerCase();
// identifiers
const KEY_TYPE_IDENTIFIER = 'aws4_request';
const SHA256_ALGORITHM_IDENTIFIER = 'AWS4-HMAC-SHA256';
const SIGNATURE_IDENTIFIER = 'AWS4';
// preset values
const EMPTY_HASH = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';
const UNSIGNED_PAYLOAD = 'UNSIGNED-PAYLOAD';

const signRequest = (request, options) => {
  const signingValues = getSigningValues(options);
  const { accessKeyId, credentialScope, longDate, sessionToken } = signingValues;
  // create the request to sign
  const headers = { ...request.headers };
  headers[HOST_HEADER] = request.url.host;
  headers[AMZ_DATE_HEADER] = longDate;
  if (sessionToken) {
      headers[TOKEN_HEADER] = sessionToken;
  }
  const requestToSign = { ...request, headers };
  // calculate and add the signature to the request
  const signature = getSignature(requestToSign, signingValues);
  const credentialEntry = `Credential=${accessKeyId}/${credentialScope}`;
  const signedHeadersEntry = `SignedHeaders=${getSignedHeaders(headers)}`;
  const signatureEntry = `Signature=${signature}`;
  headers[AUTH_HEADER] =
      `${SHA256_ALGORITHM_IDENTIFIER} ${credentialEntry}, ${signedHeadersEntry}, ${signatureEntry}`;
  return requestToSign;
};

const signUrl = async (url, options, expiration) => {

  const signingValues = getSigningValues(options);
    
  const { accessKeyId, credentialScope, longDate, sessionToken } = signingValues;
  const presignedUrl = new URL(url);
  
  Object.entries({
		[ALGORITHM_QUERY_PARAM]: SHA256_ALGORITHM_IDENTIFIER,
		[CREDENTIAL_QUERY_PARAM]: `${accessKeyId}/${credentialScope}`,
		[AMZ_DATE_QUERY_PARAM]: longDate,
		[SIGNED_HEADERS_QUERY_PARAM]: HOST_HEADER,
		...(expiration && { [EXPIRES_QUERY_PARAM]: expiration.toString() }),
		...(sessionToken && { [TOKEN_QUERY_PARAM]: sessionToken }),
	}).forEach(([key, value]) => {
		presignedUrl.searchParams.append(key, value);
	});
	const requestToSign = {
		body: undefined,
		headers: { [HOST_HEADER]: presignedUrl.host },
		method: 'GET',
		url: presignedUrl,
	};

	// calculate and add the signature to the url
	const signature = getSignature(requestToSign, signingValues);
	presignedUrl.searchParams.append(SIGNATURE_QUERY_PARAM, signature);

  return presignedUrl;
};

const getSigningValues = ({ credentials, signingDate = new Date(), signingRegion, signingService, uriEscapePath = true, }) => {
  // get properties from credentials
  const { accessKeyId, secretAccessKey, sessionToken } = credentials;
  // get formatted dates for signing
  const { longDate, shortDate } = getFormattedDates(signingDate);
  // copy header and set signing properties
  const credentialScope = getCredentialScope(shortDate, signingRegion, signingService);
  return {
      accessKeyId,
      credentialScope,
      longDate,
      secretAccessKey,
      sessionToken,
      shortDate,
      signingRegion,
      signingService,
      uriEscapePath,
  };
};

const getCredentialScope = (date, region, service) => `${date}/${region}/${service}/${KEY_TYPE_IDENTIFIER}`;

const getSignature = (request, { credentialScope, longDate, secretAccessKey, shortDate, signingRegion, signingService, uriEscapePath, }) => {
  // step 1: create a canonical request
  const canonicalRequest = getCanonicalRequest(request, uriEscapePath);
  // step 2: create a hash of the canonical request
  const hashedRequest = getHashedDataAsHex(null, canonicalRequest);
  // step 3: create a string to sign
  const stringToSign = getStringToSign(longDate, credentialScope, hashedRequest);
  // step 4: calculate the signature
  const signature = getHashedDataAsHex(getSigningKey(secretAccessKey, shortDate, signingRegion, signingService), stringToSign);
  return signature;
};

const getCanonicalRequest = ({ body, headers, method, url }, uriEscapePath = true) => [
  method,
  getCanonicalUri(url.pathname, uriEscapePath),
  getCanonicalQueryString(url.searchParams),
  getCanonicalHeaders(headers),
  getSignedHeaders(headers),
  getHashedPayload(body),
].join('\n');

const getCanonicalQueryString = (searchParams) => Array.from(searchParams)
    .sort(([keyA, valA], [keyB, valB]) => {
      if (keyA === keyB) {
        return valA < valB ? -1 : 1;
      }
      return keyA < keyB ? -1 : 1;
    })
    .map(([key, val]) => `${escapeUri(key)}=${escapeUri(val)}`)
    .join('&');

const escapeUri = (uri) => encodeURIComponent(uri).replace(/[!'()*]/g, hexEncode);
const hexEncode = (c) => `%${c.charCodeAt(0).toString(16).toUpperCase()}`;

const getCanonicalUri = (pathname, uriEscapePath = true) => pathname
    ? uriEscapePath
        ? encodeURIComponent(pathname).replace(/%2F/g, '/')
        : pathname
    : '/';

const getCanonicalHeaders = (headers) => Object.entries(headers)
    .map(([key, value]) => ({
      key: key.toLowerCase(),
      value: value?.trim().replace(/\s+/g, ' ') ?? '',
    }))
    .sort((a, b) => (a.key < b.key ? -1 : 1))
    .map(entry => `${entry.key}:${entry.value}\n`)
    .join('');

const getSignedHeaders = (headers) => Object.keys(headers)
    .map(key => key.toLowerCase())
    .sort()
    .join(';');

const getHashedPayload = (body) => {
    // return precalculated empty hash if body is undefined or null
    if (body == null) {
        return EMPTY_HASH;
    }
    if (isSourceData(body)) {
        const hashedData = getHashedDataAsHex(null, body);
        return hashedData;
    }
    // Defined body is not signable. Return unsigned payload which may or may not be accepted by the service.
    return UNSIGNED_PAYLOAD;
};

const getStringToSign = (date, credentialScope, hashedRequest) => [SHA256_ALGORITHM_IDENTIFIER, date, credentialScope, hashedRequest].join('\n');

const getSigningKey = (secretAccessKey, date, region, service) => {
  const key = `${SIGNATURE_IDENTIFIER}${secretAccessKey}`;
  const dateKey = getHashedData(key, date);
  const regionKey = getHashedData(dateKey, region);
  const serviceKey = getHashedData(regionKey, service);
  const signingKey = getHashedData(serviceKey, KEY_TYPE_IDENTIFIER);
  return signingKey;
};

const isSourceData = (body) => typeof body === 'string' || ArrayBuffer.isView(body) || isArrayBuffer(body);
const isArrayBuffer = (arg) => (typeof ArrayBuffer === 'function' && arg instanceof ArrayBuffer) ||
      Object.prototype.toString.call(arg) === '[object ArrayBuffer]';


const getFormattedDates = (date) => {
  const longDate = date.toISOString().replace(/[:-]|\.\d{3}/g, '');
  return {
      longDate,
      shortDate: longDate.slice(0, 8),
  };
};

const getHashedDataAsHex = (key, data) => {
  const hashedData = getHashedData(key, data);
  return toHex(hashedData);
};

const getHashedData = (key, data) => {
  const sha256 = new Sha256(key ?? undefined);
  sha256.update(data);
  const hashedData = sha256.digestSync();
  return hashedData;
};

export { signRequest, signUrl };