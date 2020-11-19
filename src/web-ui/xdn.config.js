module.exports = {
  routes: './xdn/routes.js',
  backends: {
    'origin': {
      domainOrIp: 'example.com',
      hostHeader: 'example.com',
    },
    'products-service': {
      domainOrIp: 'retai-loadb-xcztiko1xp2z-524701947.eu-west-1.elb.amazonaws.com',
      hostHeader: 'retai-loadb-xcztiko1xp2z-524701947.eu-west-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
    'recommendations-service': {
      domainOrIp: 'retai-loadb-1ws47hx7yw7sy-1990974172.eu-west-1.elb.amazonaws.com',
      hostHeader: 'retai-loadb-1ws47hx7yw7sy-1990974172.eu-west-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
    'carts-service': {
      domainOrIp: 'retai-loadb-3rfgyrv1kqh3-476392771.eu-west-1.elb.amazonaws.com',
      hostHeader: 'retai-loadb-3rfgyrv1kqh3-476392771.eu-west-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
  },
};
