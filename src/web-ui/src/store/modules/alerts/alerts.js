// import { ClientelingModals } from "@/partials/ClientelingModal/config";


export const alerts = {
  state: () => ({ alerts: [] }),
  mutations: {
    setAlerts: (state, { alerts }) => {
      state.alerts = alerts;
    },
    clearAlerts: (state) => {
      state.alerts = null
    }
  },
  getters: {
    numAlerts: (state) => state.alerts ? state.alerts.length : null,
    alerts: (state) => state.alerts
  }

};
