<template>
  <div class="modal-header align-items-center">
    <slot></slot>

    <button class="close" data-dismiss="modal" aria-label="close demo guide">
      <i class="fa fa-times"></i>
    </button>
  </div>
</template>

<script>
export default {
  name: 'ModalHeader',
};
</script>

<style scoped>
.modal-header {
  border-bottom: none;
}

.close {
  font-size: 1.25rem;
  opacity: 1;
  text-shadow: none;
  color: var(--grey-500);
  transition: color 150ms ease-in-out;
}

.close:focus {
  outline: none;
}

.close:hover,
.close:focus {
  color: var(--amazon-orange);
}
</style>
