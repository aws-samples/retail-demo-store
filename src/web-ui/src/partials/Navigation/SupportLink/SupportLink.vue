<template>
  <router-link to="/help" aria-label="support" class="support"><SupportIcon class="icon"></SupportIcon></router-link>
</template>

<script>
import SupportIcon from './SupportIcon';

export default {
  name: 'SupportLink',
  components: { SupportIcon },
};
</script>

<style>
.support {
  width: 40px;
}

.icon {
  transition: fill 150ms ease-in-out;
}

.support:hover .icon,
.support:focus .icon {
  fill: var(--blue-600);
}
</style>
