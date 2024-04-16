<template>
    <div class="content">
        <!-- Upload Section -->
        <div class="container">
            <div class="row">
                <div class="col">
                    <div class="vstack gap-3">
                        <label for="imageFile" class="form-label">Upload Image</label>
                        <div class="input-group p-2">
                            <input type="file" class="form-control" accept="image/*" id="imageFile" @change="handleFileSelect" aria-describedby="imageFile" aria-label="Upload">
                            <select class="form-select" v-model="selectedStyle" required>
                                <option disabled value="">Please select a style</option>
                                <option value="minimalist">Minimalist</option>
                                <option value="cozy">Cozy</option>
                                <option value="bohemian">Bohemian</option>
                                <option value="modern">Modern</option>
                                <option value="rustic">Rustic</option>
                                <option value="industrial">Industrial</option>
                                <option value="scandanavian">Scandinavian</option>
                            </select>
                            <button class="btn btn-outline-secondary" type="button" @click="generateImage" :class="{ disabled: generateButtonDisabled }">Generate</button>
                        </div>
                        <div class="progress-bar-container p-2" v-if="progress > 0">
                            <div class="progress-bar" :style="{width: `${progress}%`}"></div>
                        </div> 
                        <cropper
                            ref="cropper"
                            v-if="img"
                            :src="img"
                            class="cropper p-2"
                            imageRestriction='fill-area'
                            :moveImage=false
                            :stencil-props="{ aspectRatio: 1/1 }"
                            :default-size="defaultSize"
                            />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { v4 as uuidv4 } from 'uuid';
import { Storage } from 'aws-amplify';
import { RepositoryFactory } from "@/repositories/RepositoryFactory";
import { Cropper } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css';

const RoomsRepository = RepositoryFactory.get('rooms');

export default {
    components: {
        Cropper
    },
    props: {
        activeRoom: Object
    },
    data() {
        return {
            selectedStyle: 'minimalist',
            img: null,
            progress: 0
        }
    },
    methods: {
        async handleFileSelect(event) {
            const file = event.target.files[0];
            if (!file) {
                return;
            }
            this.$emit('file-selected');
            this.img = URL.createObjectURL(file); // Display selected image in the cropper       
        },
        defaultSize({ imageSize, visibleArea }) {
			return {
				width: (visibleArea || imageSize).width,
				height: (visibleArea || imageSize).height,
			};
		},
        async generateImage() {
            try {
                let blob = null;

                if (this.$refs.cropper) {
                    // Get the new crop result
                    const result = this.$refs.cropper.getResult();
                    if (result && result.canvas) {
                        // Create a canvas element to resize the image
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        canvas.width = 1024; // target width
                        canvas.height = 1024; // target height

                        // Calculate scaling factor to maintain aspect ratio
                        const scale = Math.min(canvas.width / result.canvas.width, canvas.height / result.canvas.height);
                        const x = (canvas.width / 2) - (result.canvas.width / 2) * scale;
                        const y = (canvas.height / 2) - (result.canvas.height / 2) * scale;

                        // Draw the resized image on the canvas
                        ctx.drawImage(result.canvas, x, y, result.canvas.width * scale, result.canvas.height * scale);

                        // Convert canvas to blob
                        await new Promise(resolve => {
                            canvas.toBlob((blobResult) => {
                                blob = blobResult;
                                resolve();
                            }, 'image/png');
                        });
                    }
                }

                if (!blob && !this.activeRoom) {
                    throw new Error('No image to upload');
                }
                let imageKey = ''
                if (blob) {
                    // Proceed with the upload process
                    const uniqueID = uuidv4();
                    const response = await Storage.put(`${uniqueID}/original.png`, blob, {
                        contentType: 'image/png',
                        level: 'private',
                        progressCallback: (progress) => {
                            this.progress = Math.round((progress.loaded / progress.total) * 100);
                        },
                    });
                    imageKey = response.key;
                    console.log('Upload successful:', response);
                } else {
                    // Use current active room for the original image
                    imageKey = this.activeRoom.image_key.split('/').slice(2).join('/');
                }
                
                this.progress = 0;
                RoomsRepository.createRoom(imageKey, this.selectedStyle.toLowerCase())
                    .then((roomId) => {
                        this.$emit('room-uploaded', roomId);
                        this.img = null;
                    });                              

            } catch (error) {
                console.error('Error during the upload or generation process:', error);
            } 
        }
    },
    computed: {
        generateButtonDisabled() {
            return this.img == null && this.activeRoom == null;
        }
    },
    watch: {
        activeRoom(newRoom) {
            if(newRoom) {
                this.selectedStyle = newRoom.room_style;
            }
        }
    }
}
</script>
<style>

.progress-bar-container {
  width: 100%;
  background-color: #f3f3f3;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.progress-bar {
  height: 20px;
  background-color: var(--blue-500);
  border-radius: 5px;
  width: 0%;
  transition: width 0.4s ease;
}

.upload-status {
  color: var(--blue-500);
  font-size: 16px;
  margin-bottom: 20px;
}
</style>