<template>
  <div class="favoriting">
      <label class="favorite_heart"
             :class="{'favorite_heart_selected': favorited, 'is-disabled': disabled}"
             >
        <input class="favorite_checkbox"
               type="checkbox"
               name="favorite"
               :value="favorited"
               :disabled="disabled"
               @click="$emit('click')"
               >
            ❤
        </label>
  </div>
</template>

<script>

export default {
  name: 'Favoriting',
  components: {},
  props: {
    'productId': {
        type: String,
        default: null
    },
    'username': {
        type: String,
        default: null
    },
    'disabled': {
        type: Boolean,
        default: false
    },
    'favorited': {
        type: Boolean,
        default: false
    }
  },
};
</script>

<style scoped>

.favoriting{
    display: inline-block
}
.favorite_heart {
    display: inline-block;
    padding-left: 0.5em;
    vertical-align: middle;
    line-height: 1;
    font-size: 2em;
    color: #ABABAB;
    cursor: pointer;
    -webkit-transition: color .2s ease-out;
    transition: color .2s ease-out;

    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}
.favorite_heart.is-disabled:hover {
     cursor: default;
 }
.favorite_checkbox {
    position: absolute;
    overflow: hidden;
    clip: rect(0 0 0 0);
    margin: -1px;
    padding: 0;
    border: 0;
}
.favorite_heart_selected{
    color: #df470b;
}
</style>
