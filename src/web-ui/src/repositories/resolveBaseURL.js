function resolveBaseURL(serviceDomain, servicePort, servicePath) {
  servicePort = servicePort || ''
  servicePath = servicePath || '/'
  return `${serviceDomain}${servicePort ? `:${servicePort}` : ''}${servicePath}`
}

export default resolveBaseURL