// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

require("dotenv").config();

const removeProtocol = (domain) => {
  try {
    return domain.replace(/https?:\/\//i, "");
  } catch (e) {
    console.error("[layer0.config.js] Invalid domain: ", domain);
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

// Build upstream endpoints
// For local dev, this should be `localhost`
// When deployed, each service should have its domain defined to the
//   ELB domain provided by AWS
const productsService = buildServiceDomain(
  process.env.VITE_PRODUCTS_SERVICE_DOMAIN,
  process.env.VITE_PRODUCTS_SERVICE_PORT
);
const recommendationsService = buildServiceDomain(
  process.env.VITE_RECOMMENDATIONS_SERVICE_DOMAIN,
  process.env.VITE_RECOMMENDATIONS_SERVICE_PORT
);
const cartsService = buildServiceDomain(
  process.env.VITE_CARTS_SERVICE_DOMAIN,
  process.env.VITE_CARTS_SERVICE_PORT
);
const usersService = buildServiceDomain(
  process.env.VITE_USERS_SERVICE_DOMAIN,
  process.env.VITE_USERS_SERVICE_PORT
);
const ordersService = buildServiceDomain(
  process.env.VITE_ORDERS_SERVICE_DOMAIN,
  process.env.VITE_ORDERS_SERVICE_PORT
);
const searchService = buildServiceDomain(
  process.env.VITE_SEARCH_SERVICE_DOMAIN,
  process.env.VITE_SEARCH_SERVICE_PORT
);
const videosService = buildServiceDomain(
  process.env.VITE_VIDEOS_SERVICE_DOMAIN,
  process.env.VITE_VIDEOS_SERVICE_PORT
);
const locationService = buildServiceDomain(
  process.env.VITE_LOCATION_SERVICE_DOMAIN,
  process.env.VITE_LOCATION_SERVICE_PORT
);
const imageService = process.env.AWS_IMAGE_SERVICE_DOMAIN;

module.exports = {
  routes: "./layer0/routes.js",
  includeFiles: {
    ".env": true,
  },
  backends: {
    "products-service": {
      domainOrIp: productsService,
      hostHeader: productsService,
      disableCheckCert: true,
    },
    "recommendations-service": {
      domainOrIp: recommendationsService,
      hostHeader: recommendationsService,
      disableCheckCert: true,
    },
    "carts-service": {
      domainOrIp: cartsService,
      hostHeader: cartsService,
      disableCheckCert: true,
    },
    "users-service": {
      domainOrIp: usersService,
      hostHeader: usersService,
      disableCheckCert: false,
    },
    "search-service": {
      domainOrIp: searchService,
      hostHeader: searchService,
      disableCheckCert: false,
    },
    "orders-service": {
      domainOrIp: ordersService,
      hostHeader: ordersService,
      disableCheckCert: false,
    },
    "videos-service": {
      domainOrIp: videosService,
      hostHeader: videosService,
      disableCheckCert: false,
    },
    "location-service": {
      domainOrIp: locationService,
      hostHeader: locationService,
      disableCheckCert: false,
    },
    "images": {
      domainOrIp: imageService,
      hostHeader: imageService,
      disableCheckCert: false,
    },
  },
};
