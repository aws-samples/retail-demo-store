import { LocalStorageKeys, getLocalStorageKey } from '../';

export const getWelcomePageVisited = getLocalStorageKey(LocalStorageKeys.WelcomePageVisited, Boolean, false);

export const setWelcomePageVisited = (isWelcomePageVisited) =>
  localStorage.setItem(LocalStorageKeys.WelcomePageVisited, isWelcomePageVisited);
