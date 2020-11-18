function resolveBaseURL(serviceDomain, servicePort, servicePath) {
  servicePort = servicePort || ''
  servicePath = servicePath || '/'
  return `${serviceDomain}${servicePort}${servicePath}`
}

export default resolveBaseURL