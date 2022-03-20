// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

function resolveBaseURL(serviceDomain, servicePort, servicePath) {
  servicePort = servicePort || ''
  servicePath = servicePath || '/'
  return `${serviceDomain}${servicePort ? `:${servicePort}` : ''}${servicePath}`
}

export default resolveBaseURL