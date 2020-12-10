export const APP_MODAL_ID = 'app-modal';

const MODAL_BREAKPOINT = 992;
const MODAL_BREAKPOINT_MOBILE_QUERY = `(max-width: ${MODAL_BREAKPOINT}px)`;

export const isMobileModalMediaQueryList = window.matchMedia(MODAL_BREAKPOINT_MOBILE_QUERY);

export const Modals = {
  DemoGuide: 'demo-guide',
  DemoWalkthrough: 'demo-walkthrough',
  ShopperSelect: 'shopper-select'
};
