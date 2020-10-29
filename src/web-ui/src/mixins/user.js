import { mapState } from 'vuex';

export const user = {
  computed: {
    ...mapState(['user']),
  },
};
