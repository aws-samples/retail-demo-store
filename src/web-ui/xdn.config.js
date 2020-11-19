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
    'users-service': {
      domainOrIp: 'retai-loadb-g60j7in33dbe-909901376.eu-west-1.elb.amazonaws.com',
      hostHeader: 'retai-loadb-g60j7in33dbe-909901376.eu-west-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
    'search-service': {
      domainOrIp: 'retai-loadb-1c7t7sjqx1n5x-779267631.eu-west-1.elb.amazonaws.com',
      hostHeader: 'retai-loadb-1c7t7sjqx1n5x-779267631.eu-west-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
    'orders-service': {
      domainOrIp: 'retai-loadb-fo4k0d8dg1p9-1518833196.eu-west-1.elb.amazonaws.com',
      hostHeader: 'retai-loadb-fo4k0d8dg1p9-1518833196.eu-west-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
  },
};
