import { mapState } from 'vuex';

export const user = {
  computed: {
    ...mapState(['user']),
    username() {
      return this.user?.username ?? 'guest'
    }
  },
};
