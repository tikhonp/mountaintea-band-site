<template>
  <div class="fullscreen">
    <div v-if="loading" class="d-flex justify-content-center align-middle my-5">
      <div class="spinner-border text-light" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <qrcode-stream :camera="camera" :torch="torch" @decode="onDecode" @init="onInit">
      <div v-if="!loading" class="container mt-3 text-center">
        <div class="card">
          <div class="card-body">
            <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
            <div v-else>
              <p v-for="i in decoded_tickets" v-if="decoded_tickets.length !== 0">{{ String(i) }}</p>
              <p v-else>Ожидание QR-кода...</p>
              <button class="btn btn-secondary" @click="changeCamera">
                <i class="fa-solid fa-camera-rotate"></i> Сменить камеру
              </button>
              <button v-if="torch_is_supported" class="btn btn-secondary" @click="torch = !torch">вкл/выкл вспышку.
              </button>
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

      decoded_tickets: [],

      loading: true,
      error: '',
    }
  },
  components: {
    QrcodeStream
  },
  methods: {
    getTicketData(url) {
      axios.get(url + 'data/', {withCredentials: true})
          .then((response) => {
            const data_to_push = {
              'type': 'done',
              'data': response.data
            }
            console.log(response)
            this.push_to_query(data_to_push)
          })
          .catch((error) => {
            const data_to_push = {
              'type': 'error',
              'data': error
            }
            this.push_to_query(data_to_push)
            console.log(error);
          })
    },
    push_to_query(element) {
      if (this.decoded_tickets.length === 3) {
        this.decoded_tickets[2] = this.decoded_tickets[1]
        this.decoded_tickets[1] = this.decoded_tickets[0]
        this.decoded_tickets[0] = element
      } else {
        this.decoded_tickets.push(element)
      }
    },
    onDecode(decodedString) {
      this.getTicketData(decodedString)
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
