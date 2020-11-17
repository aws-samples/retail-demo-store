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
  },
};
