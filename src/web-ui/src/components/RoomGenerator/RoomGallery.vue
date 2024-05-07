<template>
  <div class="gallery-container">
    <div class="mb-3 text-left">
      <h2 class="room-gallery-heading">Room Gallery</h2>
    </div>
    <div class="gallery-grid">
      <div v-for="room in rooms" :key="room.id" class="gallery-item" @click="selectRoom(room.id)">
        <RoomGalleryItem :roomStyle="room.room_style" :thumbnailKey="room.thumbnail_image_key" :is-active="room.id === activeRoom" />
      </div>
    </div>
  </div>
</template>

<script>
import RoomGalleryItem from '@/components/RoomGenerator/RoomGalleryItem.vue';

export default {
  components: {
    RoomGalleryItem
  },
  data() {
    return {
      activeRoom: null
    };
  },
  props: {
    rooms: Array,
    uploadedRoom: String
  },
  name: 'RoomGallery',
  methods: {
    selectRoom(room) {
      this.activeRoom = room
      this.$emit('room-selected', room);
    },
  },
  watch: {
    uploadedRoom(newRoom) {
      this.activeRoom = newRoom;
    }
  },
};
</script>

<style scoped>
.gallery-container {
  padding: 4px;
  margin: 0 auto;
  max-width: 896px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(128px, 128px));
  gap: 16px;
  padding: 8px;
}

.gallery-item {
  position: relative;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transition: transform 0.3s ease-in-out;
  cursor: pointer;
}

.gallery-item:hover .gallery-item-info {
  transform: translateY(0);
}

.gallery-item:hover {
  transform: scale(1.03);
}

.gallery-item:hover img {
  transform: scale(1.1);
}

.room-gallery-heading {
  font-size: 1rem;
}

@media (min-width: 768px) {
  .room-gallery-heading {
    font-size: 1.4rem;
  }
}

</style>
