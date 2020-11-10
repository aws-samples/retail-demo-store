export const parseCart = (cart) =>
  cart.items !== null
    ? cart
    : {
        ...cart,
        items: [],
      };
