// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

/*
 * Centralized handling of all analytics calls for Pinpoint, Personalize
 * (event tracker), and partner integrations.
 */
import AmplifyStore from '@/store/store';
import { fetchUserAttributes } from 'aws-amplify/auth';
import { record as personalizeRecord } from 'aws-amplify/analytics/personalize';
import Amplitude from 'amplitude-js'
import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import optimizelySDK from '@optimizely/optimizely-sdk';
import { set, event } from "vue-gtag";

const RecommendationsRepository = RepositoryFactory.get('recommendations')
const ProductsRepository = RepositoryFactory.get('products')

// Log analytics data to console, until code updated to push to Kinesis
const record = (data) => console.debug(data)
const identifyUser = (data) => console.debug(data);

export const AnalyticsHandler = {
    clearUser() {
        if (this.amplitudeEnabled()) {
            // Update Amplitude user
            Amplitude.getInstance().setUserId(null)
            Amplitude.getInstance().regenerateDeviceId()
        }
        if (this.mParticleEnabled()) {
            var identityCallback = function() {
             window.mParticle.logEvent(
                        'Logout',
                        window.mParticle.EventType.Transaction, {}
                    );
            };
            window.mParticle.Identity.logout({}, identityCallback);
           }
    },

    async identify(user) {
        if (!user) {
            return Promise.resolve()
        }

        var promise

        try {
            let endpoint = {
                userId: user.id,
                userProfile: {
                    customProperties: {},
                },
                options: {
                    userAttributes: {
                        Username: [ user.username ],
                        ProfileEmail: [ user.email ],
                        FirstName: [ user.first_name ],
                        LastName: [ user.last_name ],
                        Gender: [ user.gender ],
                        Age: [ user.age.toString() ],
                        Persona: user.persona.split("_")
                    }
                },
            }

            if (user.sign_up_date) {
                endpoint.userProfile.customProperties.SignUpDate = [ user.sign_up_date ]
            }

            if (user.last_sign_in_date) {
                endpoint.userProfile.customProperties.LastSignInDate = [ user.last_sign_in_date ]
            }

            if (user.addresses && user.addresses.length > 0) {
                let address = user.addresses[0]
                endpoint.userProfile.location = {
                    city: address.city,
                    country: address.country,
                    postalCode: address.zipcode,
                    region: address.state
                }
            }

            if (this.mParticleEnabled()) {

                let identityRequest = {
                    userIdentities: {
                        email: user.email,
                        customerid: user.username
                    }
                };

                let identityCallback = function(result) {
                    if (result.getUser()) {
                        //proceed with login
                        let currentUser = result.getUser();
                        currentUser.setUserAttribute("$FirstName", user.first_name);
                        currentUser.setUserAttribute("$LastName", user.last_name);
                        currentUser.setUserAttribute("$Gender", user.gender);
                        currentUser.setUserAttribute("$Age", user.age);
                        currentUser.setUserAttribute("amazonPersonalizeId", user.id);
                        currentUser.setUserAttribute("Persona", user.persona);
                        currentUser.setUserAttribute("SignUpDate", user.sign_up_date);
                        currentUser.setUserAttribute("LastSignInDate", user.last_sign_in_date);
                        if (user.addresses && user.addresses.length > 0) {
                            let address = user.addresses[0]
                            currentUser.setUserAttribute("$City", address.city);
                            currentUser.setUserAttribute("$Country", address.country);
                            currentUser.setUserAttribute("$Zip", address.zipcode);
                            currentUser.setUserAttribute("$State", address.state);
                        }
                        window.mParticle.logEvent(
                            'Set User',
                            window.mParticle.EventType.Transaction, {}
                        );

                    }
                };
                window.mParticle.Identity.login(identityRequest, identityCallback);
            }
            const { email } = await fetchUserAttributes();
            if (email) {
                endpoint.userProfile.email = email
                promise = identifyUser(endpoint)
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

        if (this.personalizeEventTrackerEnabled()) {
            personalizeRecord({
                eventType: "Identify",
                properties: {
                    "userId": user.id
                }
            })
        }

        if (this.segmentEnabled()) {
            let userProperties = {
                username: user.username,
                email: user.email,
                firstName: user.first_name,
                lastName: user.last_name,
                gender: user.gender,
                age: user.age,
                persona: user.persona
            };
            window.analytics.identify(user.id, userProperties);
        }

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

        if (this.googleAnalyticsEnabled()) {
            set({
                "user_id": user.id,
                "user_properties": {
                    "age": user.age,
                    "gender": user.gender,
                    "persona": user.persona
                }
            });
        }

        return promise
    },

    userSignedUp(user) {
        if (user) {
            record({
                name: 'UserSignedUp',
                attributes: {
                    userId: user.id,
                    signUpDate: user.sign_up_date
                }
            })

            if (this.googleAnalyticsEnabled()) {
                event("sign_up", {
                    "method": "Web"
                });
            }

            if (this.mParticleEnabled()) {
                window.mParticle.logEvent('UserSignedUp', window.mParticle.EventType.Transaction, { "method": "Web" });
               }
        }
    },

    userSignedIn(user) {
        if (user) {
            record({
                name: 'UserSignedIn',
                attributes: {
                    userId: user.id,
                    signInDate: user.last_sign_in_date
                }
            })

            if (this.googleAnalyticsEnabled()) {
                event("login", {
                    "method": "Web"
                });
            }

            if (this.mParticleEnabled()) {
                window.mParticle.logEvent('UserSignedIn', window.mParticle.EventType.Transaction, { "method": "Web" });
               }
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

            if (this.googleAnalyticsEnabled()) {
                event("exp_" + experiment.feature, {
                    "feature": experiment.feature,
                    "name": experiment.name,
                    "variation": experiment.variationIndex
                });
            }
        }
    },

    productAddedToCart(user, cart, product, quantity, feature, experimentCorrelationId) {
        if (user) {
            record({
                name: 'AddToCart',
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

            identifyUser({
                userId: user.id,
                options: {
                    userAttributes: {
                        HasShoppingCart: ['true']
                    },
                },
                metrics: {
                    ItemsInCart: cart.items.length
                }
            })
        }

        if (this.personalizeEventTrackerEnabled()) {
            personalizeRecord({
                eventType: 'AddToCart',
                userId: user ? user.id : AmplifyStore.state.provisionalUserID,
                properties: {
                    itemId: product.id,
                    discount: "No"
                }
            })
            AmplifyStore.commit('incrementSessionEventsRecorded');
        }

        let eventProperties = {
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
        };

        if (this.segmentEnabled()) {
            window.analytics.track('AddToCart', eventProperties);
        }

        if (this.mParticleEnabled()) {
            let productName = product.name;
            let productId = product.id;
            let productPrice = product.price;

            let productDetails = window.mParticle.eCommerce.createProduct(
                productName,
                productId,
                parseFloat(productPrice),
                quantity
            );
            let totalAmount = productPrice * quantity;
            let transactionAttributes = {
                Id: cart.id,
                Revenue: totalAmount,
                Tax: totalAmount * .10
            };

            let customAttributes = {
                mpid: window.mParticle.Identity.getCurrentUser().getMPID(),
                cartId: cart.id,
                category: product.category,
                image: product.image,
                feature: feature,
                experimentCorrelationId: experimentCorrelationId
            };

            // Send details of viewed product to mParticle
            window.mParticle.eCommerce.logProductAction(window.mParticle.ProductActionType.AddToCart, productDetails, customAttributes, {}, transactionAttributes);
        }

        if (this.amplitudeEnabled()) {
            Amplitude.getInstance().logEvent('AddToCart', eventProperties);
        }

        if (user && this.optimizelyEnabled()) {
            const optimizelyClientInstance = this.optimizelyClientInstance();
            const expectedRevisionNumber = optimizelyClientInstance.configObj.revision;
            if (this.isOptimizelyDatafileSynced(expectedRevisionNumber)) {
                const userId = user.id.toString();
                optimizelyClientInstance.track('AddToCart', userId);
            }
        }

        if (this.googleAnalyticsEnabled()) {
            event('add_to_cart', {
                "currency": "USD",
                "value": +product.price.toFixed(2),
                "items": [
                  {
                    "item_id": product.id,
                    "item_name": product.name,
                    "item_category": product.category,
                    "quantity": quantity,
                    "currency": "USD",
                    "price": +product.price.toFixed(2)
                  }
                ]
            });
        }
    },
   async recordShoppingCart (user, cart) {
        if (user && cart) {
            const hasItem = cart.items.length > 0
            var productImages, productTitles, productURLs
            if (hasItem) {
                const cartItem = await ProductsRepository.getProduct(cart.items[0].product_id);
                productImages = [cartItem.image]
                productTitles = [cartItem.name]
                productURLs = [cartItem.url]
            } else {
                productImages = []
                productTitles = []
                productURLs = []
            }
            identifyUser({
                userId: user.id,
                options: {
                    userAttributes: {
                        WebsiteCartURL : [import.meta.env.VITE_WEB_ROOT_URL + '#/cart'],
                        WebsiteLogoImageURL : [import.meta.env.VITE_WEB_ROOT_URL + '/RDS_logo_white.svg'],
                        WebsitePinpointImageURL : [import.meta.env.VITE_WEB_ROOT_URL + '/icon_Pinpoint_orange.svg'],
                        ShoppingCartItemImageURL:  productImages,
                        ShoppingCartItemTitle :  productTitles,
                        ShoppingCartItemURL : productURLs,
                        HasShoppingCart: hasItem ? ['true'] : ['false']
                    }
                }
            })
            return hasItem
        } else {
            return false;
        }
    },
    async recordAbanonedCartEvent(user, cart) {
        const hasItem = await this.recordShoppingCart(user, cart)
        var productImages, productTitles, productURLs
        if (hasItem) {

            if (this.mParticleEnabled()) {

                const cartItem = await ProductsRepository.getProduct(cart.items[0].product_id);
                productImages = [cartItem.image]
                productTitles = [cartItem.name]
                productURLs = [cartItem.url]

                let customAttributes = {
                   mpid: window.mParticle.Identity.getCurrentUser().getMPID(),
                   HasShoppingCart: cart.items.length > 0 ? true : false,
                   WebsiteCartURL: import.meta.env.VITE_WEB_ROOT_URL + '#/cart',
                   WebsiteLogoImageURL: import.meta.env.VITE_WEB_ROOT_URL + '/RDS_logo_white.svg',
                   WebsitePinpointImageURL: import.meta.env.VITE_WEB_ROOT_URL + '/icon_Pinpoint_orange.svg',
                   ShoppingCartItemImageURL: productImages,
                   ShoppingCartItemTitle: productTitles,
                   ShoppingCartItemURL: productURLs,
               };
               window.mParticle.logEvent('AbandonedCartEvent',window.mParticle.EventType.Transaction, customAttributes);
            }

            record({
                name: '_session.stop',
            })
        }
    },

    productRemovedFromCart(user, cart, cartItem, origQuantity) {
        if (user && user.id) {
            record({
                name: 'RemoveFromCart',
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

            identifyUser({
                userId: user.id,
                options: {
                    userAttributes: {
                        HasShoppingCart: cart.items.length > 0 ? ['true'] : ['false']
                    },
                },
                metrics: {
                    ItemsInCart: cart.items.length
                }
            })
        }

        let eventProperties = {
            cartId: cart.id,
            productId: cartItem.product_id,
            quantity: origQuantity,
            price: +cartItem.price.toFixed(2)
        };

        if (this.mParticleEnabled()) {
            let product1 = window.mParticle.eCommerce.createProduct(
                cartItem.product_name, // Name
                cartItem.product_id, // SKU
                cartItem.price, // Price
                origQuantity // Quantity
            );

            window.mParticle.eCommerce.logProductAction(window.mParticle.ProductActionType.RemoveFromCart, product1, {mpid: window.mParticle.Identity.getCurrentUser().getMPID()},{},{});
        }

        if (this.segmentEnabled()) {
            window.analytics.track('RemoveFromCart', eventProperties);
        }

        if (this.amplitudeEnabled()) {
            Amplitude.getInstance().logEvent('RemoveFromCart', eventProperties);
        }


        if (this.googleAnalyticsEnabled()) {
            event('remove_from_cart', {
                "currency": "USD",
                "value": +cartItem.price.toFixed(2),
                "items": [
                  {
                    "item_id": cartItem.product_id,
                    "item_name": cartItem.product_name,
                    "quantity": origQuantity,
                    "currency": "USD",
                    "price": +cartItem.price.toFixed(2)
                  }
                ]
            });
        }
    },

    productQuantityUpdatedInCart(user, cart, cartItem, change) {
        if (user && user.id) {
            record({
                name: 'UpdateQuantity',
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

        if (this.personalizeEventTrackerEnabled()) {
            personalizeRecord({
                eventType: 'UpdateQuantity',
                userId: user ? user.id : AmplifyStore.state.provisionalUserID,
                properties: {
                    itemId: cartItem.product_id,
                    discount: "No"
                }
            })
            AmplifyStore.commit('incrementSessionEventsRecorded');
        }

        let eventProperties = {
            cartId: cart.id,
            productId: cartItem.product_id,
            quantity: cartItem.quantity,
            change: change,
            price: +cartItem.price.toFixed(2)
        };

        if (this.mParticleEnabled()) {
            let product1 = window.mParticle.eCommerce.createProduct(
            cartItem.product_name, // Name
            cartItem.product_id, // SKU
            cartItem.price, // Price
            cartItem.quantity // Quantity
        );

            window.mParticle.eCommerce.logProductAction(window.mParticle.ProductActionType.AddToCart, product1, {mpid: window.mParticle.Identity.getCurrentUser().getMPID()},{},{});
        }

        if (this.segmentEnabled()) {
            window.analytics.track('UpdateQuantity', eventProperties);
        }

        if (this.amplitudeEnabled()) {
            Amplitude.getInstance().logEvent('UpdateQuantity', eventProperties);
        }
    },
    productViewed(user, product, feature, experimentCorrelationId, discount) {
        if (user) {
            record({
                name: 'View',
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

        if (this.personalizeEventTrackerEnabled()) {
            personalizeRecord({
                eventType: 'View',
                userId: user ? user.id : AmplifyStore.state.provisionalUserID,
                properties: {
                    itemId: product.id,
                    discount: discount?"Yes":"No"
                }
            });
            AmplifyStore.commit('incrementSessionEventsRecorded');
        }

        if (experimentCorrelationId) {
            RecommendationsRepository.recordExperimentOutcome(experimentCorrelationId)
        }

        let eventProperties = {
            productId: product.id,
            name: product.name,
            category: product.category,
            image: product.image,
            feature: feature,
            experimentCorrelationId: experimentCorrelationId,
            price: +product.price.toFixed(2)
        };

        if (this.segmentEnabled()) {
            window.analytics.track('View', eventProperties);
        }

        if (this.mParticleEnabled()) {
            let productDetails = window.mParticle.eCommerce.createProduct(
               product.name,
               product.id,
               parseFloat(product.price.toFixed(2)),
               1
           );
           window.mParticle.eCommerce.logProductAction(window.mParticle.ProductActionType.ViewDetail, productDetails,{mpid: window.mParticle.Identity.getCurrentUser().getMPID()},{},{});
        }

        if (this.amplitudeEnabled()) {
            Amplitude.getInstance().logEvent('View', eventProperties);
        }

        if (user && this.optimizelyEnabled()) {
            const optimizelyClientInstance = this.optimizelyClientInstance();
            const expectedRevisionNumber = optimizelyClientInstance.configObj.revision;
            if (this.isOptimizelyDatafileSynced(expectedRevisionNumber)) {
                const userId = user.id.toString();
                optimizelyClientInstance.track('View', userId);
            }
        }

        if (this.googleAnalyticsEnabled()) {
            event('view_item', {
                "currency": "USD",
                "value": +product.price.toFixed(2),
                "items": [
                  {
                    "item_id": product.id,
                    "item_name": product.name,
                    "item_category": product.category,
                    "quantity": 1,
                    "currency": "USD",
                    "price": +product.price.toFixed(2)
                  }
                ]
            });
        }
    },

    cartViewed(user, cart, cartQuantity, cartTotal) {
        if (user) {
            record({
                name: 'ViewCart',
                attributes: {
                    userId: user.id,
                    cartId: cart.id
                },
                metrics: {
                    cartTotal: +cartTotal.toFixed(2),
                    cartQuantity: cartQuantity
                }
            })
        }

        if (this.personalizeEventTrackerEnabled()) {
            for (var item in cart.items) {
                personalizeRecord({
                    eventType: 'ViewCart',
                    userId: user ? user.id : AmplifyStore.state.provisionalUserID,
                    properties: {
                        itemId: cart.items[item].product_id,
                        discount: "No"
                    }
                })
                AmplifyStore.commit('incrementSessionEventsRecorded');
            }
        }

        let eventProperties = {
            cartId: cart.id,
            cartTotal: +cartTotal.toFixed(2),
            cartQuantity: cartQuantity
        };

        if (this.segmentEnabled()) {
            window.analytics.track('ViewCart', eventProperties);
        }

        if (this.mParticleEnabled()) {
             var cartViewList = [];
             let totalAmount = 0;

             for (var cartCounter = 0; cartCounter < cart.items.length; cartCounter++) {
                 var cartViewItem = cart.items[cartCounter];
                 var cartViewDetails = window.mParticle.eCommerce.createProduct(
                     cartViewItem.product_name,
                     cartViewItem.product_id,
                     parseFloat(cartViewItem.price),
                     parseInt(cartViewItem.quantity)
                 );
                 totalAmount = totalAmount + parseFloat(cartViewItem.price);
                 cartViewList.push(cartViewDetails);
             }

             let transactionAttributes = {
                 Id: cart.id,
                 Revenue: totalAmount,
                 Tax: totalAmount * .10
             };
             window.mParticle.eCommerce.logProductAction(window.mParticle.ProductActionType.Click, cartViewList, {mpid: window.mParticle.Identity.getCurrentUser().getMPID()}, {}, transactionAttributes);
         }

        if (this.amplitudeEnabled()) {
            // Amplitude event
            Amplitude.getInstance().logEvent('ViewCart', eventProperties);
        }

        if (this.googleAnalyticsEnabled()) {
            let gaItems = [];
            for (var i in cart.items) {
                gaItems.push({
                    "item_id": cart.items[i].product_id,
                    "item_name": cart.items[i].product_name,
                    "quantity": cart.items[i].quantity,
                    "index": gaItems.length + 1,
                    "currency": "USD",
                    "price": +cart.items[i].price.toFixed(2)
                });
            }

            event('view_cart', {
                "value": +cartTotal.toFixed(2),
                "currency": "USD",
                "items": gaItems
            });
        }
    },

    checkoutStarted(user, cart, cartQuantity, cartTotal) {
        if (user) {
            record({
                name: 'StartCheckout',
                attributes: {
                    userId: user.id,
                    cartId: cart.id
                },
                metrics: {
                    cartTotal: +cartTotal.toFixed(2),
                    cartQuantity: cartQuantity
                }
            })
        }

        if (this.personalizeEventTrackerEnabled()) {
            for (var item in cart.items) {
                personalizeRecord({
                    eventType: 'StartCheckout',
                    userId: user ? user.id : AmplifyStore.state.provisionalUserID,
                    properties: {
                        itemId: cart.items[item].product_id,
                        discount: "No"
                    }
                })
                AmplifyStore.commit('incrementSessionEventsRecorded');
            }
        }

        let eventProperties = {
            cartId: cart.id,
            cartTotal: +cartTotal.toFixed(2),
            cartQuantity: cartQuantity
        };

        if (this.segmentEnabled()) {
            window.analytics.track('StartCheckout', eventProperties);
        }

        if (this.mParticleEnabled()) {
            let totalAmount = 0;
            var checkoutList = [];
            for (var z = 0; z < cart.items.length; z++) {
                var checkoutItem = cart.items[z];
                var checkoutDetails = window.mParticle.eCommerce.createProduct(
                    checkoutItem.product_name,
                    checkoutItem.product_id,
                    parseFloat(checkoutItem.price),
                    parseInt(checkoutItem.quantity)
                );
                totalAmount = totalAmount + parseFloat(checkoutItem.price);
                checkoutList.push(checkoutDetails);
            }

            let transactionAttributes = {
                Id: cart.id,
                Revenue: totalAmount,
                Tax: totalAmount * .10
            };
            window.mParticle.eCommerce.logProductAction(window.mParticle.ProductActionType.Checkout, checkoutList, {mpid: window.mParticle.Identity.getCurrentUser().getMPID()}, {}, transactionAttributes);
        }

        if (this.amplitudeEnabled()) {
            Amplitude.getInstance().logEvent('StartCheckout', eventProperties);
        }

        if (this.googleAnalyticsEnabled()) {
            let gaItems = [];
            for (var i in cart.items) {
                gaItems.push({
                    "item_id": cart.items[i].product_id,
                    "item_name": cart.items[i].product_name,
                    "quantity": cart.items[i].quantity,
                    "index": gaItems.length + 1,
                    "currency": "USD",
                    "price": +cart.items[i].price.toFixed(2)
                });
            }

            event('begin_checkout', {
                "value": +cartTotal.toFixed(2),
                "currency": "USD",
                "items": gaItems
            });
        }
    },

    orderCompleted(user, cart, order) {
        if (user) {
            record({
                name: 'Purchase',
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
                record({
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

            if (this.personalizeEventTrackerEnabled()) {
                personalizeRecord({
                    eventType: 'Purchase',
                    userId: user ? user.id : AmplifyStore.state.provisionalUserID,
                    properties: {
                        itemId: orderItem.product_id,
                        discount: "No"
                    }
                })
                AmplifyStore.commit('incrementSessionEventsRecorded');
            }

            if (this.amplitudeEnabled()) {
                // Amplitude revenue
                let revenue = new Amplitude.Revenue()
                    .setProductId(orderItem.product_id.toString())
                    .setPrice(+orderItem.price.toFixed(2))
                    .setQuantity(orderItem.quantity);
                Amplitude.getInstance().logRevenueV2(revenue);
            }
        }

        if (user && user.id) {
            identifyUser({
                userId: user.id,
                options: {
                    userAttributes: {
                        HasShoppingCart: ['false'],
                        HasCompletedOrder: ['true']
                    },
                },
                metrics: {
                    ItemsInCart: 0
                }
            })
        }

        if (this.mParticleEnabled()) {
            var orderList = [];
            let totalAmount = 0;
            for (var x = 0; x < cart.items.length; x++) {
                var orderItem = cart.items[x];
                var orderDetails = window.mParticle.eCommerce.createProduct(
                    orderItem.product_name,
                    orderItem.product_id,
                    parseFloat(orderItem.price),
                    parseInt(orderItem.quantity)
                );
                totalAmount = totalAmount + parseFloat(orderItem.price);
                orderList.push(orderDetails);
            }

            let transactionAttributes = {
                Id: cart.id,
                Revenue: totalAmount,
                Tax: totalAmount * .10
            };

            let customAttributes = {mpid: window.mParticle.Identity.getCurrentUser().getMPID()}

            if (order.promo_code != null && order.promo_code != "")
                customAttributes = { promo_code: order.promo_code };


            window.mParticle.eCommerce.logProductAction(window.mParticle.ProductActionType.Purchase, orderList, customAttributes, {}, transactionAttributes);
        }

        let eventProperties = {
            cartId: cart.id,
            orderId: order.id,
            orderTotal: +order.total.toFixed(2)
        };

        if (this.segmentEnabled()) {
            window.analytics.track('Purchase', eventProperties);
        }

        if (this.amplitudeEnabled()) {
            Amplitude.getInstance().logEvent('Purchase', eventProperties);
        }

        if (this.googleAnalyticsEnabled()) {
            let gaItems = [];
            for (var i in order.items) {
                gaItems.push({
                    "item_id": order.items[i].product_id,
                    "item_name": order.items[i].product_name,
                    "quantity": order.items[i].quantity,
                    "index": gaItems.length + 1,
                    "currency": "USD",
                    "price": +order.items[i].price.toFixed(2)
                });
            }

            event('purchase', {
                "transaction_id": order.id.toString(),
                "value": +order.total.toFixed(2),
                "currency": "USD",
                "items": gaItems
            });
        }
    },

    productSearched(user, query, numResults) {
        if (user && user.id) {
            record({
                name: 'Search',
                attributes: {
                    userId: user ? user.id : null,
                    query: query,
                    reranked: (user ? 'true' : 'false')
                },
                metrics: {
                    resultCount: numResults
                }
            })

            identifyUser({
                userId: user.id,
                userProfile: {
                    customProperties: {
                        HashPerformedSearch: ['true']
                    }
                }
            })
        }

        let eventProperties = {
            query: query,
            reranked: (user ? 'true' : 'false'),
            resultCount: numResults
        };

        if (this.segmentEnabled()) {
            window.analytics.track('Search', eventProperties);
        }

        if (this.mParticleEnabled()) {
            let customAttributes = {
                resultCount: numResults,
                mpid: window.mParticle.Identity.getCurrentUser().getMPID(),
                query: query,
                reranked: (user ? 'true' : 'false')
            };
            window.mParticle.logEvent('Search',window.mParticle.EventType.Transaction, customAttributes);

        }

        if (this.amplitudeEnabled()) {
            Amplitude.getInstance().logEvent('Search', eventProperties);
        }

        if (this.googleAnalyticsEnabled()) {
            event('search', {
                "search_term": query
            });
        }
    },

    personalizeEventTrackerEnabled() {
        return import.meta.env.VITE_PERSONALIZE_TRACKING_ID && import.meta.env.VITE_PERSONALIZE_TRACKING_ID != 'NONE';
    },

    segmentEnabled() {
        return import.meta.env.VITE_SEGMENT_WRITE_KEY && import.meta.env.VITE_SEGMENT_WRITE_KEY != 'NONE';
    },

    amplitudeEnabled() {
        return import.meta.env.VITE_AMPLITUDE_API_KEY && import.meta.env.VITE_AMPLITUDE_API_KEY != 'NONE';
    },

    optimizelyEnabled() {
        return !!import.meta.env.VITE_OPTIMIZELY_SDK_KEY && import.meta.env.VITE_OPTIMIZELY_SDK_KEY != 'NONE';
    },

    mParticleEnabled() {
        return import.meta.env.VITE_MPARTICLE_API_KEY && import.meta.env.VITE_MPARTICLE_API_KEY != 'NONE';
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
            this._optimizelyClientInstance = optimizelySDK.createInstance({ sdkKey: import.meta.env.VITE_OPTIMIZELY_SDK_KEY });
        }
        return this._optimizelyClientInstance;
    },

    googleAnalyticsEnabled() {
        return import.meta.env.VITE_GOOGLE_ANALYTICS_ID && import.meta.env.VITE_GOOGLE_ANALYTICS_ID != 'NONE';
    },
}
