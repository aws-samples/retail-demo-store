module.exports = {
  routes: './xdn/routes.js',
  backends: {
    'origin': {
      domainOrIp: 'example.com',
      hostHeader: 'example.com',
    },
    'products-service': {
      domainOrIp: 'retai-loadb-16dliebv5x2k0-1293237675.us-east-1.elb.amazonaws.com',
      hostHeader: 'retai-loadb-16dliebv5x2k0-1293237675.us-east-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
    'recommendations-service': {
      domainOrIp: 'retai-loadb-1gqnv9ena4pnm-1501839280.us-east-1.elb.amazonaws.com',
      hostHeader: 'retai-loadb-1gqnv9ena4pnm-1501839280.us-east-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
    'carts-service': {
      domainOrIp: 'retai-loadb-gflsv8hfji23-2065367342.us-east-1.elb.amazonaws.com',
      hostHeader: 'retai-loadb-gflsv8hfji23-2065367342.us-east-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
    'users-service': {
      domainOrIp: 'retai-loadb-1rp9gbburu8uw-238221144.us-east-1.elb.amazonaws.com',
      hostHeader: 'retai-loadb-1rp9gbburu8uw-238221144.us-east-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
    'search-service': {
      domainOrIp: 'retai-loadb-3s2vnzqs9tia-2084066377.us-east-1.elb.amazonaws.com',
      hostHeader: 'retai-loadb-3s2vnzqs9tia-2084066377.us-east-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
    'orders-service': {
      domainOrIp: 'retai-loadb-l7344battsk2-1994211820.us-east-1.elb.amazonaws.com',
      hostHeader: 'retai-loadb-l7344battsk2-1994211820.us-east-1.elb.amazonaws.com',
      disableCheckCert: true,
    },
  },
};
