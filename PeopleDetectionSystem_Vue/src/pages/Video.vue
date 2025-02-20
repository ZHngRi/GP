<template>
  <!-- 显示视频流 -->
  <div class="con">
    <video v-for='camera in data.cameras' :key="camera.id" width="540px" height="320px" :id="'video'+camera.id" class="video-js vjs-default-skin" autoplay muted preload="auto">
      <source :src="`http://localhost/hls/${camera.id}.m3u8`" type="application/x-mpegURL" >
    </video>
  </div>
</template>

<script>
import { reactive, onMounted, onBeforeUnmount } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'Video',
  setup() {
    const store = useStore()
    const data = reactive({
      cameras: store.state.camera
    })

    function initVideoSource(cameraId) {
      videojs(cameraId, {
        bigPlayButton: false,
        textTrackDisplay: false,
        posterImage: false,
        errorDisplay: false,
        controlBar: true
        // ...其他配置参数
      }, function () {
        this.play()
      })
    }

    onMounted(() => {
      data.cameras.forEach(camera => {
        initVideoSource('video' + camera.id)
      })
    })

    // 在组件销毁前清理 video.js 实例
    onBeforeUnmount(() => {
      data.cameras.forEach(camera => {
        const player = videojs('video' + camera.id);
        if (player) {
          player.dispose(); // 销毁 video.js 实例
        }
      })
    })


    return {
      data
    }
  }
}
</script>

<style scoped>
.con {
  display: flex;
  flex-wrap: wrap;
}

.video-js {
  margin: 0px;
}
</style>
