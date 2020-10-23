// simulate enum till we move to TS
export const LocalStorageKeys = {
  WelcomePageVisited: 'WELCOME_PAGE_VISITED',
};

export const getLocalStorageKey = (key, validator, defaultValue) => () => {
  const valueFromLocalStorage = localStorage.getItem(key);

  try {
    const parsedValue = JSON.parse(valueFromLocalStorage);

    if (validator(parsedValue)) return parsedValue;
    // handling the catch case below
    // eslint-disable-next-line no-empty
  } catch {}

  if (defaultValue === undefined) return null;

  localStorage.setItem(key, defaultValue);

  return defaultValue;
};
