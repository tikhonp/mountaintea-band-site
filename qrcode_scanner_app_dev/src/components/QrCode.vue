<template>
  <div class="fullscreen">
    <div v-if="loading" class="d-flex justify-content-center align-middle my-5">
      <div class="spinner-border text-light" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <qrcode-stream :camera="camera" :torch="torch" @decode="onDecode" @init="onInit">
      <div v-if="!loading" class="container mt-3">
        <div class="card">
          <div class="card-body">
            <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
            <div v-else>
              <p v-if="decoded_string">{{ decoded_string }}</p>
              <button class="btn btn-secondary" @click="changeCamera">Сменить камеру.</button>
              <button class="btn btn-secondary" v-if="torch_is_supported" @click="torch = !torch">вкл/выкл вспышку.</button>
            </div>
          </div>
        </div>
      </div>
    </qrcode-stream>
  </div>
</template>

<script>
import {QrcodeStream} from 'vue3-qrcode-reader'

export default {
  data() {
    return {
      camera: 'auto',
      torch: false,

      torch_is_supported: false,
      decoded_string: '',

      loading: true,
      error: '',
    }
  },
  components: {
    QrcodeStream
  },
  methods: {
    onDecode(decodedString) {
      this.decoded_string = decodedString
    },
    changeCamera() {
      if (this.camera === 'rear' || this.camera === 'auto') {
        this.camera = 'front'
      } else {
        this.camera = 'rear'
      }
    },
    async onInit(promise) {
      this.error = ""
      try {
        const {capabilities} = await promise
        this.torch_is_supported = !!capabilities.torch
      } catch (error) {
        if (error.name === 'NotAllowedError') {
          this.error = "Чтобы продолжить, перезагрузите страницу и разрешите доступ к камере."
        } else if (error.name === 'NotFoundError') {
          this.error = "У вас нет камеры."
        } else if (error.name === 'NotSupportedError') {
          this.error = "Страница не загружена через HTTPS или localhost."
        } else if (error.name === 'NotReadableError') {
          this.error = "Возможно ваша камера используется другим приложением, проверьте и перезагрузите страницу."
        } else if (error.name === 'OverconstrainedError') {
          this.error = "Вы пытались включить фронтальную камеру несмотря на то, что ее нет?"
        } else if (error.name === 'StreamApiNotSupportedError') {
          this.error = "Ваш браузер не поддерживается."
        }
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style>
.fullscreen {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background-color: black;
  display: flex;
  flex-flow: column nowrap;
  justify-content: center;
}
</style>
