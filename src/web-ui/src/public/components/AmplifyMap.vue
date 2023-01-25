<template>
  <div id="mapContainer" ref="mapContainer" class="large-map"></div>
</template>

<script>
import mapbox from 'mapbox-gl';
import "mapbox-gl/dist/mapbox-gl.css";
import {Credentials, Signer} from "@aws-amplify/core";
import Location from "@/location/Location";

const resourceName = import.meta.env.VITE_LOCATION_RESOURCE_NAME;
const locationApi = new Location();

export default {
  name: "AmplifyMap",
  props: {
    devicePositions: {
      type: Array,
      default: () => []
    },
    routes: {
      type: Array,
      default: () => []
    },
    storePosition: {
      type: Array,
      default: () => [0, 0]
    },
    zoom: {
      type: Number,
      default: () => 14
    },
  },
  data () {
    return {
      map: null,
      mapLoaded: false
    }
  },
  mounted () {
    this.getCreds()
  },
  methods: {
    getCreds() {
      Credentials.get()
        .then(creds => this.creds = creds)
        .then(this.loadMap)
    },
    async loadMap() {
      if (!this.storePosition) {
        return
      }
      console.log(this.$refs)
      const mapContainer = this.$refs.mapContainer
      this.map = new mapbox.Map({
        attributionControl: false,
        center: this.storePosition || [0, 0],
        container: mapContainer,
        transformRequest: this.transformMapboxRequest,
        style: `geo://${resourceName}`,
        zoom: this.zoom
      });

      this.map.once('load', async () => {
        this.mapLoaded = true;
        this.map.resize();
        this.loadGeofence();
        this.renderCustomerPositions();
        this.renderStorePosition();
        this.renderCustomerRoutes();
      })

    },
    async loadGeofence() {
      const geofences = await locationApi.getGeofences();

      const source = this.map.getSource('geofences');
      // Remove source & layer when there aren't geofences
      if (source && !geofences.length) {
        this.map.removeLayer('geofences');
        this.map.removeSource('geofences');
        return;
      }

      const data = {
        type: 'FeatureCollection',
        features: geofences.Entries.map(feature => ({
          id: feature.GeofenceId,
          type: 'Feature',
          geometry: {
            type: 'Polygon',
            coordinates: feature.Geometry.Polygon
          },
          properties: {},
        })),
      };

      if (source) {
        source.setData(data);
      }
      else {
        this.map.addSource('geofences', { type: 'geojson', data });
        this.map.addLayer({
          id: 'geofences',
          filter: ['==', '$type', 'Polygon'],
          paint: { 'fill-color': '#0073bb', 'fill-opacity': 0.15 },
          source: 'geofences',
          type: 'fill',
        });
      }
    },
    async renderCustomerPositions() {
      if (!this.map || !this.map.isStyleLoaded() || !this.devicePositions?.length) {
        return;
      }
      const source = this.map.getSource('devices');
      if (source && !this.devicePositions) {
        this.map.removeLayer('devices');
        this.map.removeSource('devices');
        return;
      }

      const data = {
        type: 'FeatureCollection',
        features: this.devicePositions.map((position) => ({
          geometry: {
            coordinates: position,
            type: 'Point',
          },
          type: 'Feature',
        })),
      };

      if (source) {
        source.setData(data);
      }
      else {
        this.map.addSource('devices', { type: 'geojson', data });
        this.map.addLayer({
          id: 'devices',
          paint: { 'circle-radius': 12, 'circle-color': '#B42222' },
          source: 'devices',
          type: 'circle',
        });
      }
    },
    async renderStorePosition() {
      if (!this.map) {
        return;
      }
      const source = this.map.getSource('stores');
      if (source && this.storePosition) {
        this.map.removeLayer('stores');
        this.map.removeSource('stores');
        return;
      }

      const data = {
        type: 'Feature',
        geometry: {
          coordinates: this.storePosition,
          type: 'Point',
        }
      };
      if (source) {
        source.setData(data);
      }

      else {
        this.map.addSource('stores', { type: 'geojson', data });
        this.map.addLayer({
          id: 'stores',
          paint: { 'circle-radius': 12, 'circle-color': '#2242b4' },
          source: 'stores',
          type: 'circle',
        });
      }
    },
    async renderCustomerRoutes() {
      if (!this.map || !this.routes?.length) {
        return;
      }
      const source = this.map.getSource('routes');
      if (source && this.routes) {
        this.map.removeLayer('routes');
        this.map.removeSource('routes');
        return;
      }

      const data = {
        type: 'FeatureCollection',
        features: this.routes.map((route) => ({
          geometry: {
            coordinates: route,
            type: 'LineString',
          },
          type: 'Feature',
        })),
      };
      if (source) {
        source.setData(data);
      }
      else {
        this.map.addSource('routes', { type: 'geojson', data });
        this.map.addLayer({
          id: 'routes',
          paint: { 'line-color': '#49b03e', 'line-width': 2},
          source: 'routes',
          type: 'line',
        });
      }
    },
    transformMapboxRequest(url, resourceType) {
      let newUrl = url;
      const resourceTypeAccept = {
        Style: 'application/json',
        Tile: 'application/octet-stream',
        SpriteImage: 'image/webp,*/*',
        Glyphs: 'application/octet-stream',
      };
      const headers = {
        accept: resourceTypeAccept[resourceType] || 'application/json',
      };

      if (resourceType === 'Style' && newUrl.startsWith('geo://')) {
        const [, resourceName] = newUrl.split('geo://');
        newUrl = `https://maps.geo.${import.meta.env.VITE_AWS_REGION}.amazonaws.com/maps/v0/maps/${resourceName}/style-descriptor`;
      }

      if (!newUrl.includes('amazonaws.com')) {
        return {
          url: newUrl,
          headers,
        };
      }
      return Signer.sign(
          { headers, method: 'GET', url: newUrl },
          {
            access_key: this.creds.accessKeyId,
            secret_key: this.creds.secretAccessKey,
            session_token: this.creds.sessionToken,
          }
      );
    }
  },
  watch: {
    devicePositions: function () {
      this.renderCustomerPositions();
    },
    storePosition: function () {
      if (!this.mapLoaded && this.creds) {
        this.loadMap();
      }
    }
  }
}
</script>

<style scoped>

.large-map {
  height: 100%;
  width: 100%;
}

</style>