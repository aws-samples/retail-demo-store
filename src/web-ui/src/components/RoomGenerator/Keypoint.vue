<template>
  <div>
    <div v-for="(label, index) in labels"
      :key="`keypoint-${index}`"
      class="keypoint"
      :style="calculateKeypointStyle(label)"
      @click="selectKeypoint(label)" />
  </div>
  </template>
  
  <script>
  export default {
    name: 'Keypoint',
    props: {
      labels: Array,
      containerDimensions: Object,
      highlightedBoundingBox: Object,
    },
    emits: ['keypoint-selected'],
    methods: {
      calculateKeypointStyle(label) {
        const boundingBox = label.bounding_box;
        const containerWidth = this.containerDimensions.width;
        const containerHeight = this.containerDimensions.height;
        const left = boundingBox.Left * containerWidth;
        const top = boundingBox.Top * containerHeight;
        const width = boundingBox.Width * containerWidth;
        const height = boundingBox.Height * containerHeight;
  
        const centerX = left + width / 2;
        const centerY = top + height / 2;
  
        let style = {
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
  
        // Apply highlighted style if this keypoint's bounding box matches the highlightedBoundingBox
        if (this.highlightedBoundingBox && this.compareBoundingBoxes(boundingBox, this.highlightedBoundingBox)) {
          style = { ...style, border: '3px solid yellow' }; // Example of highlighted style
        }
  
        return style;
      },
      selectKeypoint(label) {
        this.$emit('keypoint-selected', label);
      },
      compareBoundingBoxes(boundingBox1, boundingBox2) {
        // Simple comparison based on bounding box properties
        return boundingBox1.Left === boundingBox2.Left && boundingBox1.Top === boundingBox2.Top && boundingBox1.Width === boundingBox2.Width && boundingBox1.Height === boundingBox2.Height;
      }
    },
  };
  </script>
  
  <style scoped>
  .keypoint {
    position: absolute;
    width: 40px;
    height: 40px;
    opacity: 70%;
    border-radius: 50%;
    background-color: var(--blue-500);
    transform: translate(-50%, -50%);
  }
  </style>
  