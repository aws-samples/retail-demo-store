// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

require('dotenv').config();

const removeProtocol = (domain) => {
  try {
    return domain.replace(/https?:\/\//i, '');
  } catch (e) {
    console.error('[xdn.config.js] Invalid domain: ', domain);
    throw new Error(e.message);
  }
};

const buildServiceDomain = (domain, port) => {
  let serviceDomain = removeProtocol(domain);
  if (port) {
    serviceDomain += `:${port}`;
  }
  return serviceDomain;
};

const productsService = buildServiceDomain(process.env.VUE_APP_PRODUCTS_SERVICE_DOMAIN, process.env.VUE_APP_PRODUCTS_SERVICE_PORT);
const recommendationsService = buildServiceDomain(process.env.VUE_APP_RECOMMENDATIONS_SERVICE_DOMAIN, process.env.VUE_APP_RECOMMENDATIONS_SERVICE_PORT);
const cartsService = buildServiceDomain(process.env.VUE_APP_CARTS_SERVICE_DOMAIN, process.env.VUE_APP_CARTS_SERVICE_PORT);
const usersService = buildServiceDomain(process.env.VUE_APP_USERS_SERVICE_DOMAIN, process.env.VUE_APP_USERS_SERVICE_PORT);
const ordersService = buildServiceDomain(process.env.VUE_APP_ORDERS_SERVICE_DOMAIN, process.env.VUE_APP_ORDERS_SERVICE_PORT);
const searchService = buildServiceDomain(process.env.VUE_APP_SEARCH_SERVICE_DOMAIN, process.env.VUE_APP_SEARCH_SERVICE_PORT);
const videosService = buildServiceDomain(process.env.VUE_APP_VIDEOS_SERVICE_DOMAIN, process.env.VUE_APP_VIDEOS_SERVICE_PORT);

module.exports = {
  routes: './xdn/routes.js',
  backends: {
    'products-service': {
      domainOrIp: productsService,
      hostHeader: productsService,
      disableCheckCert: true,
    },
    'recommendations-service': {
      domainOrIp: recommendationsService,
      hostHeader: recommendationsService,
      disableCheckCert: true,
    },
    'carts-service': {
      domainOrIp: cartsService,
      hostHeader: cartsService,
      disableCheckCert: true,
    },
    'users-service': {
      domainOrIp: usersService,
      hostHeader: usersService,
      disableCheckCert: true,
    },
    'search-service': {
      domainOrIp: searchService,
      hostHeader: searchService,
      disableCheckCert: true,
    },
    'orders-service': {
      domainOrIp: ordersService,
      hostHeader: ordersService,
      disableCheckCert: true,
    },
    'videos-service': {
      domainOrIp: videosService,
      domainOrIp: videosService,
      disableCheckCert: true,
    },
  },
};
