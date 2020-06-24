// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/* 
 * Centralized handling of all analytics calls for Pinpoint, Personalize 
 * (event tracker), and partner integrations.
 */
import Vue from 'vue';
import { Analytics as AmplifyAnalytics } from '@aws-amplify/analytics';
import Amplitude from 'amplitude-js'
import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import optimizelySDK from '@optimizely/optimizely-sdk';

const RecommendationsRepository = RepositoryFactory.get('recommendations')

export const AnalyticsHandler = {
    clearUser() {
        if (this.amplitudeEnabled()) {
            // Update Amplitude user
            Amplitude.getInstance().setUserId(null)
            Amplitude.getInstance().regenerateDeviceId()
        }
    },

    async identify(user) {
        if (!user) {
            return Promise.resolve()            
        }

        var promise

        try {
            const cognitoUser = await Vue.prototype.$Amplify.Auth.currentAuthenticatedUser()

            let endpoint = {
                userId: user.id,
                optOut: 'NONE',
                userAttributes: {
                    Username: [ user.username ],
                    ProfileEmail: [ user.email ],
                    FirstName: [ user.first_name ],
                    LastName: [ user.last_name ],
                    Gender: [ user.gender ],
                    Age: [ user.age.toString() ],
                    Persona: user.persona.split("_")
                },
                attributes: {}
            }

            if (user.sign_up_date) {
                endpoint.attributes.SignUpDate = [ user.sign_up_date ]
            }

            if (user.last_sign_in_date) {
                endpoint.attributes.LastSignInDate = [ user.last_sign_in_date ]
            }
    
            if (user.addresses && user.addresses.length > 0) {
                let address = user.addresses[0]
                endpoint.location = {
                    City: address.city,
                    Country: address.country,
                    PostalCode: address.zipcode,
                    Region: address.state
                }
            }
    
            if (cognitoUser.attributes.email) {
                endpoint.address = cognitoUser.attributes.email
                endpoint.channelType = 'EMAIL'
                promise = AmplifyAnalytics.updateEndpoint(endpoint)
            }
            else {
                promise = Promise.resolve()
            }
        }
        catch(error) {
            // eslint-disable-next-line
            console.log(error)
            promise = Promise.reject(error)
        }
         
        AmplifyAnalytics.record({
            eventType: "Identify",
            properties: {
                "userId": user.id
            }
        }, 'AmazonPersonalize')

        if (this.amplitudeEnabled()) {
            // Amplitude identify call
            Amplitude.getInstance().setUserId(user.id);
            // Should we be doing this. Need to support case of switching 
            // users and not getting sessions confused.
            Amplitude.getInstance().regenerateDeviceId();

            var identify = new Amplitude.Identify()
                .set('username', user.username)
                .set('email', user.email)
                .set('firstName', user.first_name)
                .set('lastName', user.last_name)
                .set('gender', user.gender)
                .set('age', user.age)
                .set('persona', user.persona)

            if (user.sign_up_date) {
                identify.setOnce('signUpDate', user.sign_up_date)
            }

            if (user.last_sign_in_date) {
                identify.set('lastSignInDate', user.last_sign_in_date)
            }

            Amplitude.getInstance().identify(identify)
        }

        return promise
    },

    userSignedUp(user) {
        if (user) {
            AmplifyAnalytics.record({
                name: 'UserSignedUp', 
                attributes: { 
                    userId: user.id,
                    signUpDate: user.sign_up_date
                }
            })
        }
    },

    userSignedIn(user) {
        if (user) {
            AmplifyAnalytics.record({
                name: 'UserSignedIn', 
                attributes: { 
                    userId: user.id,
                    signInDate: user.last_sign_in_date
                }
            })
        }
    },

    identifyExperiment(user, experiment) {
        if (experiment) {
            if (this.amplitudeEnabled()) {
                var identify = new Amplitude.Identify()
                    .set(experiment.feature + '.' + experiment.name, experiment.variationIndex)
                    .set(experiment.feature + '.' + experiment.name + '.id', experiment.correlationId);
                Amplitude.getInstance().identify(identify);
            }

            if (user && this.optimizelyEnabled()) {
                const optimizelyClientInstance = this.optimizelyClientInstance();
                const expectedRevisionNumber = optimizelyClientInstance.configObj.revision;
                if (this.isOptimizelyDatafileSynced(expectedRevisionNumber)) {
                    const userId = user.id.toString();
                    optimizelyClientInstance.activate(experiment.experiment_key, userId);
                }
            }
        }
    },

    productAddedToCart(user, cart, product, quantity, feature, experimentCorrelationId) {
        if (user) {
            AmplifyAnalytics.record({
                name: 'ProductAdded', 
                attributes: { 
                    userId: user.id,
                    cartId: cart.id,
                    productId: product.id,
                    name: product.name,
                    category: product.category,
                    image: product.image,
                    feature: feature,
                    experimentCorrelationId: experimentCorrelationId
                },
                metrics: {
                    quantity: quantity,
                    price: +product.price.toFixed(2)
                }
            })

            AmplifyAnalytics.updateEndpoint({
                userId: user.id,
                attributes: {
                    HasShoppingCart: ['true']
                },
                metrics: {
                    ItemsInCart: cart.items.length
                }
            })
        }

        AmplifyAnalytics.record({
            eventType: 'ProductAdded',
            userId: user ? user.id : null,
            properties: {
                itemId: product.id
            }
        }, 'AmazonPersonalize')

        if (this.amplitudeEnabled()) {
            Amplitude.getInstance().logEvent('ProductAdded', {
                userId: user ? user.id : null,
                cartId: cart.id,
                productId: product.id,
                name: product.name,
                category: product.category,
                image: product.image,
                feature: feature,
                experimentCorrelationId: experimentCorrelationId,
                quantity: quantity,
                price: +product.price.toFixed(2)
            })
        }

        if (user && this.optimizelyEnabled()) {
            const optimizelyClientInstance = this.optimizelyClientInstance();
            const expectedRevisionNumber = optimizelyClientInstance.configObj.revision;
            if (this.isOptimizelyDatafileSynced(expectedRevisionNumber)) {
                const userId = user.id.toString();
                optimizelyClientInstance.track('ProductAdded', userId);
            }
        }
    },

    productRemovedFromCart(user, cart, cartItem, origQuantity) {
        if (user && user.id) {
            AmplifyAnalytics.record({
                name: 'ProductRemoved', 
                attributes: { 
                    userId: user.id,
                    cartId: cart.id,
                    productId: cartItem.product_id
                },
                metrics: {
                    quantity: origQuantity,
                    price: +cartItem.price.toFixed(2)
                }
            })

            AmplifyAnalytics.updateEndpoint({
                userId: user.id,
                attributes: {
                    HasShoppingCart: cart.items.length > 0 ? ['true'] : ['false']
                },
                metrics: {
                    ItemsInCart: cart.items.length
                }
            })
        }

        if (this.amplitudeEnabled()) {
            // Amplitude event
            var eventProperties = {
                cartId: cart.id,
                productId: cartItem.product_id,
                quantity: origQuantity,
                price: +cartItem.price.toFixed(2)
            };
            Amplitude.getInstance().logEvent('ProductRemoved', eventProperties);      
        }
    },

    productQuantityUpdatedInCart(user, cart, cartItem, change) {
        if (user && user.id) {
            AmplifyAnalytics.record({
                name: 'ProductQuantityUpdated', 
                attributes: { 
                    userId: user.id,
                    cartId: cart.id,
                    productId: cartItem.product_id
                },
                metrics: {
                    quantity: cartItem.quantity,
                    change: change,
                    price: +cartItem.price.toFixed(2)
                }
            })
        }

        AmplifyAnalytics.record({
            eventType: 'ProductQuantityUpdated',
            userId: user ? user.id : null,
            properties: {
                itemId: cartItem.product_id
            }
        }, 'AmazonPersonalize')

        if (this.amplitudeEnabled()) {
            // Amplitude event
            var eventProperties = {
                cartId: cart.id,
                productId: cartItem.product_id,
                quantity: cartItem.quantity,
                change: change,
                price: +cartItem.price.toFixed(2)
            };
            Amplitude.getInstance().logEvent('ProductQuantityUpdated', eventProperties);
        }
    },

    productViewed(user, product, feature, experimentCorrelationId) {
        if (user) {
            AmplifyAnalytics.record({
                name: 'ProductViewed', 
                attributes: { 
                    userId: user.id,
                    productId: product.id,
                    name: product.name,
                    category: product.category,
                    image: product.image,
                    feature: feature,
                    experimentCorrelationId: experimentCorrelationId
                },
                metrics: {
                    price: +product.price.toFixed(2)
                }
            })
        }
  
        AmplifyAnalytics.record({
            eventType: 'ProductViewed',
            userId: user ? user.id : null,
            properties: {
                itemId: product.id
            }
        }, 'AmazonPersonalize');

        if (experimentCorrelationId) {
            RecommendationsRepository.recordExperimentOutcome(experimentCorrelationId)
        }

        if (this.amplitudeEnabled()) {
            // Amplitude event
            var eventProperties = {
                productId: product.id,
                name: product.name,
                category: product.category,
                image: product.image,
                feature: feature,
                experimentCorrelationId: experimentCorrelationId,
                price: +product.price.toFixed(2)
            };
            Amplitude.getInstance().logEvent('ProductViewed', eventProperties);
        }

        if (user && this.optimizelyEnabled()) {
            const optimizelyClientInstance = this.optimizelyClientInstance();
            const expectedRevisionNumber = optimizelyClientInstance.configObj.revision;
            if (this.isOptimizelyDatafileSynced(expectedRevisionNumber)) {
                const userId = user.id.toString();
                optimizelyClientInstance.track('ProductViewed', userId);
            }
        }
    },

    cartViewed(user, cart, cartQuantity, cartSubTotal, cartTotal) {
        if (user) {
            AmplifyAnalytics.record({
                name: 'CartViewed', 
                attributes: { 
                    userId: user.id,
                    cartId: cart.id
                },
                metrics: {
                    cartSubTotal: +cartSubTotal.toFixed(2),
                    cartTotal: +cartTotal.toFixed(2),
                    cartQuantity: cartQuantity
                }
            })
        }

        for (var item in cart.items) {
            AmplifyAnalytics.record({
                eventType: 'CartViewed',
                userId: user ? user.id : null,
                properties: {
                    itemId: cart.items[item].product_id
                }
            }, 'AmazonPersonalize')
        }

        if (this.amplitudeEnabled()) {
            // Amplitude event
            var eventProperties = {
                cartId: cart.id,
                cartSubTotal: +cartSubTotal.toFixed(2),
                cartTotal: +cartTotal.toFixed(2),
                cartQuantity: cartQuantity
            };
            Amplitude.getInstance().logEvent('CartViewed', eventProperties);      
        }
    },

    checkoutStarted(user, cart, cartQuantity, cartSubTotal, cartTotal) {
        if (user) {
            AmplifyAnalytics.record({
                name: 'CheckoutStarted', 
                attributes: { 
                    userId: user.id,
                    cartId: cart.id
                },
                metrics: {
                    cartSubTotal: +cartSubTotal.toFixed(2),
                    cartTotal: +cartTotal.toFixed(2),
                    cartQuantity: cartQuantity
                }
            })
        }
    
        for (var item in cart.items) {
            AmplifyAnalytics.record({
                eventType: 'CheckoutStarted',
                userId: user ? user.id : null,
                properties: {
                    itemId: cart.items[item].product_id
                }
            }, 'AmazonPersonalize')
        }

        if (this.amplitudeEnabled()) {
            // Amplitude event
            var eventProperties = {
                cartId: cart.id,
                cartSubTotal: +cartSubTotal.toFixed(2),
                cartTotal: +cartTotal.toFixed(2),
                cartQuantity: cartQuantity
            };
            Amplitude.getInstance().logEvent('CheckoutStarted', eventProperties);      
        }
    },

    orderCompleted(user, cart, order) {
        if (user) {
            AmplifyAnalytics.record({
                name: 'OrderCompleted', 
                attributes: { 
                    userId: user.id,
                    cartId: cart.id,
                    orderId: order.id.toString()
                },
                metrics: {
                    orderTotal: +order.total.toFixed(2)
                }
            })
        }
  
        for (var itemIdx in order.items) {
            let orderItem = order.items[itemIdx]
  
            if (user) {
                AmplifyAnalytics.record({
                    name: '_monetization.purchase', 
                    attributes: { 
                        userId: user.id,
                        cartId: cart.id,
                        orderId: order.id.toString(),
                        _currency: 'USD',
                        _product_id: orderItem.product_id
                    },
                    metrics: {
                        _quantity: orderItem.quantity,
                        _item_price: +orderItem.price.toFixed(2)
                    }
                })
            }
  
            AmplifyAnalytics.record({
                eventType: 'OrderCompleted',
                userId: user ? user.id : null,
                properties: {
                    itemId: orderItem.product_id
                }
            }, 'AmazonPersonalize')

            if (this.amplitudeEnabled()) {
                // Amplitude revenue
                var revenue = new Amplitude.Revenue()
                    .setProductId(orderItem.product_id.toString())
                    .setPrice(+orderItem.price.toFixed(2))
                    .setQuantity(orderItem.quantity);
                Amplitude.getInstance().logRevenueV2(revenue);
            }
        }

        if (user && user.id) {
            AmplifyAnalytics.updateEndpoint({
                userId: user.id,
                attributes: {
                    HasShoppingCart: ['false'],
                    HasCompletedOrder: ['true']
                },
                metrics: {
                    ItemsInCart: 0
                }
            })
        }

        if (this.amplitudeEnabled()) {
            // Amplitude event
            var eventProperties = {
                cartId: cart.id,
                orderId: order.id,
                orderTotal: +order.total.toFixed(2)
            };
            Amplitude.getInstance().logEvent('OrderCompleted', eventProperties);
        }
    },

    productSearched(user, query, numResults) {
        if (user && user.id) {
            AmplifyAnalytics.record({
                name: 'ProductSearched', 
                attributes: { 
                    userId: user ? user.id : null,
                    query: query,
                    reranked: (user ? 'true' : 'false')
                },
                metrics: {
                    resultCount: numResults
                }
            })

            AmplifyAnalytics.updateEndpoint({
                userId: user.id,
                attributes: {
                    HashPerformedSearch: ['true']
                }
            })
        }

        if (this.amplitudeEnabled()) {
            // Amplitude event
            var eventProperties = {
                query: query,
                reranked: (user ? 'true' : 'false'),
                resultCount: numResults
            };
            Amplitude.getInstance().logEvent('ProductSearched', eventProperties);
        }
    },

    amplitudeEnabled() {
        return process.env.VUE_APP_AMPLITUDE_API_KEY && process.env.VUE_APP_AMPLITUDE_API_KEY != 'NONE'
    },

    optimizelyEnabled() {
        return !!process.env.OPTIMIZELY_SDK_KEY && process.env.OPTIMIZELY_SDK_KEY !== 'NONE';
    },

    isOptimizelyDatafileSynced(expectedRevisionNumber) {
        if (!this.optimizelyEnabled()) {
            return false;
        }
        const optimizelyClientInstance = this.optimizelyClientInstance();
        return optimizelyClientInstance.configObj.revision !== expectedRevisionNumber;
    },

    optimizelyClientInstance() {
        if (!this._optimizelyClientInstance && this.optimizelyEnabled()) {
            this._optimizelyClientInstance = optimizelySDK.createInstance({ sdkKey: process.env.OPTIMIZELY_SDK_KEY });
        }
        return this._optimizelyClientInstance;
    },
}