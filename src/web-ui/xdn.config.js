module.exports = {
  routes: './xdn/routes.js',
  backends: {
    'origin': {
      domainOrIp: 'example.com',
      hostHeader: 'example.com',
    },
    'products-service': {
      domainOrIp: 'retai-LoadB-XCZTIKO1XP2Z-524701947.eu-west-1.elb.amazonaws.com',
      hostHeader: 'retai-LoadB-XCZTIKO1XP2Z-524701947.eu-west-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
  },
};
