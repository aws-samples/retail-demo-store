export const getProductImageUrl = (product) => {
  if (!product.image) return `${process.env.VUE_APP_IMAGE_ROOT_URL}/product_image_coming_soon.png`;

  if (product.image.includes('://')) return product.image;

  return `${process.env.VUE_APP_IMAGE_ROOT_URL}${product.category}/${product.image}`;
};
