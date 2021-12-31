<template>
  <div class="favoriting">
      <label class="favorite_heart"
             :class="{'favorite_heart_selected': value, 'is-disabled': disabled}"
             >
        <input class="favorite_checkbox"
               type="checkbox"
               name="favorite"
               :value="value"
               :disabled="disabled"
               @click="toggleFavorite"
               ><!-- v-model="value" -->
            ❤
        </label>
  </div>
</template>

<script>

import {RepositoryFactory} from "@/repositories/RepositoryFactory";
const FavoritingRepository = RepositoryFactory.get('favoriting');

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
    }
  },
  data: function () { return {
      'value': {
          type: Boolean,
          default: false
      },
    }
  },
  created: async function () {
    const { data } = await FavoritingRepository.getIsFavorited(this.username, this.productId)
    this.value = data["isFavorited"]
    if (this.value) {
      console.log(`${this.username} has favourited ${this.productId}`)
    } else {
      console.log(`${this.username} has not favourited ${this.productId}`)
    }
  },
  methods: {
      toggleFavorite: function() {
          if (this.disabled===true) {
              return;
          }
          this.value = !this.value
          FavoritingRepository.setIsFavorited(this.username, this.productId, this.value)
          console.log(`Favourite for user ${this.username} and product ${this.productId} is now ${this.value}!`)
      }
  },
  computed: { },
};
</script>

<style scoped>

.favoriting{
    display: inline-block
}
.favorite_heart {
    display: inline-block;
    /*padding: 10px;*/
    padding-left: 0.5em;
    vertical-align: middle;
    line-height: 1;
    /*font-size: 16px;*/
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
   /* height: 1px;
    width: 1px; */
    margin: -1px;
    padding: 0;
    border: 0;
}
.favorite_heart_selected{
    color: #df470b;
}
</style>
