export const capitalize = (value) => {
  if (!value) return '';

  const str = String(value);

  return str.charAt(0).toUpperCase() + str.slice(1);
};
