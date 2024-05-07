<template>
  <Layout>
    <div class="content">
      <div class="container">
        <h2 class="m-0 text-left">Room Makeover</h2>
        <div class="row">
          <div class="col">
            <ImageUpload :activeRoom="activeRoom" @file-selected="onFileSelected" @room-uploaded="onRoomUploaded"/>
          </div>
        </div>
        <div class="row">
          <div class="col-6">
            <div class="d-flex justify-content-center" v-if="showSpinner">
              <div class="spinner-border" role="status" />
            </div>
          </div>
          <div class="col-2">
            <p>{{statusMessage}}</p>
          </div>
        </div>
        <div class="row">
          <div class="col-10">    
              <div v-if="bothImagesLoaded && activeRoom" class="relative-container" ref="imageContainer">
                <VueCompareImage :leftImage="imageCompare.left" :rightImage="imageCompare.right" />
                <Keypoint :labels="activeRoom?.labels" :containerDimensions="containerDimensions" :highlightedBoundingBox="highlightedBoundingBox" @keypoint-selected="selectKeypoint" />
                <div v-if="highlightedBoundingBox" :style="highlightedBoundingBoxStyle" class="highlighted-bounding-box"></div>
              </div>
          </div>
          <div class="col-2">
            <SimilarProducts :itemIds="matchingProducts"/>
          </div>
        </div>
        <div class="row">
          <div class="col">
            <RoomGallery :rooms="rooms" :uploadedRoom="uploadedRoomId" @room-selected="onRoomSelected"/>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from "@/components/Layout/Layout.vue";
import { RepositoryFactory } from "@/repositories/RepositoryFactory";
import { VueCompareImage } from 'vue3-compare-image';
import RoomGallery from '@/components/RoomGenerator/RoomGallery.vue';
import Keypoint from '@/components/RoomGenerator/Keypoint.vue';
import SimilarProducts from "@/components/RoomGenerator/SimilarProducts.vue";
import ImageUpload from "@/components/RoomGenerator/ImageUpload.vue";
import { downloadImageS3 } from '../util/downloadImageS3';

const RoomsRepository = RepositoryFactory.get('rooms');

export default {
  components: {
    Layout,
    RoomGallery,
    VueCompareImage,
    Keypoint,
    SimilarProducts,
    ImageUpload
  },
  name: 'RoomGenerator',
  data() {
    return {
      rooms: [],
      activeRoom: null,
      uploadedRoomId: null,
      imageCompare: {left: null, right: null},
      bothImagesLoaded: false,
      statusMessage: '',
      highlightedBoundingBox: null,
      highlightedBoundingBoxStyle: {},
      matchingProducts: [],
      showSpinner: false,
      containerDimensions: { width: 0, height: 0 },
      keypointStyles: {}
    };
  },
  created() {
    this.getRooms();
  },
  mounted() {
    this.debouncedHandleResize = this.debounce(this.handleResize);
    window.addEventListener('resize', this.debouncedHandleResize);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.debouncedHandleResize);
  },
  methods: {
    onFileSelected() {
      this.activeRoom = null;
      this.uploadedRoomId = null;
      this.matchingProducts = [];
    },
    onRoomUploaded(roomId) {
      const fetchRoomAndUpdate = async (id, count) => {
        this.showSpinner = true;
        this.uploadedRoomId = id;
        RoomsRepository.getRoom(id)
          .then((room) => {
            this.statusMessage = room.room_state
            if (room.room_state === 'Done') {
              this.showSpinner = false;
              this.activeRoom = room;
              this.statusMessage = '';
              this.getRooms();
            } else {
              // Five second interval * 20 = 100 seconds timeout
              if (count < 20) {
                setTimeout(fetchRoomAndUpdate, 5000, id, ++count);
              } else {
                this.showSpinner = false;
                // This could be because of an error or Autoscaling has scaled down to zero
                // If autoscaling has kicked in, wait 5-10 mins for this to resume
                this.statusMessage = 'Timed Out Waiting for Room Generation';
                console.log("Timed out waiting for room generation.");
              }
            }
          })
      };
      fetchRoomAndUpdate(roomId, 1);
      this.getRooms();
    },
    onRoomSelected(room) {
      console.log('New active room:', room)
      this.matchingProducts = []
      RoomsRepository.getRoom(room)
        .then((room) => this.activeRoom = room)
    },
    getRooms() {
      RoomsRepository.getRooms()
        .then((rooms) => this.rooms = rooms)
    },
    calculateKeyPointStyles() {
      // Assuminx
      this.activeRoom?.labels?.forEach((label, index) => {
        this.updateKeypointStyle(index, label.bounding_box);
      });
    },
    updateKeypointStyle(index, boundingBox) {
      const { containerWidth, containerHeight } = this.containerDimensions;
      const style = this.calculateKeyPointStyle(boundingBox, containerWidth, containerHeight);
      this.keypointStyles[index] = style;
    },
    imageLoaded() {
      this.$nextTick(() => {
        const checkVueCompareImageLoaded = () => {
        const container = this.$refs.imageContainer;
        const containerWidth = container.offsetWidth;
        const containerHeight = container.offsetWidth;
        console.log(container.offsetHeight)
        if (container && containerWidth > 0 && containerHeight > 0) {
          this.containerDimensions = { width: containerWidth, height: containerHeight };
          // Recalculate keypoint styles based on the new dimensions
          this.updateBoundingBoxStyle();
          this.calculateKeyPointStyles();
        } else {
          // Retry after a short delay
          setTimeout(checkVueCompareImageLoaded, 100);
        }
      };
      checkVueCompareImageLoaded();
      });
    },
    calculateKeyPointStyle(boundingBox, containerWidth, containerHeight) {
      // Convert bounding box percentages to actual pixel values based on the container size
      const left = boundingBox.Left * containerWidth;
      const top = boundingBox.Top * containerHeight;
      const width = boundingBox.Width * containerWidth;
      const height = boundingBox.Height * containerHeight;

      // Calculate the center of the bounding box
      const centerX = left + width / 2;
      const centerY = top + height / 2;

      // Prepare and return the style object for the keypoint
      // Note: The keypoint element is positioned at its center, hence the translation adjustments
      return {
        position: 'absolute',
        left: `${centerX}px`,
        top: `${centerY}px`,
        width: `30px`,
        height: `30px`,
        transform: 'translate(-50%, -50%)',
        borderRadius: '50%',
        backgroundColor: 'var(--blue-500)',
        cursor: 'pointer',
        border: '2px solid white',
      };
    },
    selectKeypoint(keypoint) {
      this.highlightBoundingBox(keypoint.bounding_box);
      this.matchingProducts = keypoint.similar_items
        
    },
    highlightBoundingBox(boundingBox) {
        this.componentKey = Date.now();
        this.highlightedBoundingBox = boundingBox;
        this.updateBoundingBoxStyle();
    },
    updateBoundingBoxStyle() {
      if (!this.highlightedBoundingBox) {
        this.highlightedBoundingBoxStyle = null;
        return;
      }

      const containerWidth = this.$refs.imageContainer?.offsetWidth;
      const containerHeight = this.$refs.imageContainer?.offsetHeight;

      const style = {
        left: `${this.highlightedBoundingBox.Left * containerWidth}px`,
        top: `${this.highlightedBoundingBox.Top * containerHeight}px`,
        width: `${this.highlightedBoundingBox.Width * containerWidth}px`,
        height: `${this.highlightedBoundingBox.Height * containerHeight}px`,
      };

      this.highlightedBoundingBoxStyle = style;
    },
  debounce(func, timeout = 300){
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
  },
  handleResize() {
    this.updateBoundingBoxStyle();
    if (this.$refs.imageContainer) {
      const { offsetWidth, offsetHeight } = this.$refs.imageContainer;
      this.containerDimensions = { width: offsetWidth, height: offsetHeight };
      this.calculateKeyPointStyles(); // Recalculate keypoint positions
    }
  },
  },
  watch: {
    activeRoom(newRoom) {
      if(newRoom) {
        const imageKey = newRoom.image_key.split('/').slice(2).join('/');
        const newImageKey = newRoom.final_image_key.split('/').slice(2).join('/');
        const images = {left: null, right: null}
        const original = downloadImageS3(imageKey)
          .then((url) => images.left = url)
        const final = downloadImageS3(newImageKey)
          .then((url) => images.right = url)
        Promise.all([original, final])
          .then(() => {
            this.imageCompare = images
            this.bothImagesLoaded = true
            this.imageLoaded()
            this.highlightedBoundingBoxStyle = null;
            this.highlightedBoundingBox = null;
        })
      }
    }
  },
};
</script>

<style>
.main-container {
  display: flex;
  justify-content: space-between;
}

.content-container {
  flex: 1;
  max-width: 1024px;
}

.relative-container {
  position: relative;
}

.highlighted-bounding-box {
  position: absolute;
  opacity: 50%;
  border: 5px solid white;
  border-radius: 5px;
  box-sizing: border-box;
  pointer-events: none;
}

</style>