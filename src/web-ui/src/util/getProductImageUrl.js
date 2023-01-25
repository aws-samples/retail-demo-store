export const getProductImageUrl = (product) => {
  if (!product.image) return `${import.meta.env.VITE_IMAGE_ROOT_URL}/product_image_coming_soon.png`;

  if (product.image.includes('://')) return product.image;

  return `${import.meta.env.VITE_IMAGE_ROOT_URL}${product.category}/${product.image}`;
};
