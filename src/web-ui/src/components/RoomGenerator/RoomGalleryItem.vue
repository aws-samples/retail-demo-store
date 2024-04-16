<template>
    <div :class="{ active: isActive }">
        <img alt="Room Preview" class="room-preview" :src="thumbnailImage"/>
        <div class="gallery-item-info">
            <p>{{ roomStyle }}</p>
        </div>
    </div>
</template>
<script>
import { downloadImageS3 } from '../../util/downloadImageS3';

const resolveThumbnail = (component) => {
    if (component.thumbnailKey) {
        const key = component.thumbnailKey.split('/').slice(2).join('/');
        downloadImageS3(key)
            .then((url) => component.thumbnailImage = url)
    }
}

export default {
  props: {
    roomStyle: String,
    thumbnailKey: String,
    isActive: Boolean
  },
  name: 'RoomGalleryItem',
  data() {
    return {
        thumbnailImage: "/no_image.png",
    }
  },
  created() {
    resolveThumbnail(this);
  },
  watch: {
    thumbnailKey(newVal) {
      if (newVal) {
        resolveThumbnail(this);
      }
    }
  }
};
</script>
<style scoped>

.room-preview { /* Adjusted to use generic img styling for consistency */
  width: 100%;
  height: auto;
  object-fit: cover;
  transition: transform 0.3s ease-in-out;
}

.gallery-item-info {
  border: blue;
  border-radius: 0dvh;
}
.active {
    border-width: medium;
    border-style: solid;
    border-color: blue;
}

</style>