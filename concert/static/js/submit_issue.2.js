function validEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

const issues_app = Vue.createApp({
    delimiters: ['[[',']]'],
    data() {
        return {
            title: '',
            description: '',
            telegram: '',
            email: '',

            titleClass: 'form-control',
            descriptionClass: 'form-control',
            telegramClass: 'form-control',
            emailClass: 'form-control',
            alertClass: 'alert mt-5 alert-secondary',

            title_invalid: '',
            description_invalid: '',
            telegram_invalid: '',
            email_invalid: '',

            is_done: false,
            loading: false,

            submitButtonDisabled: false,
        }
    },
    methods: {
        warnDisabled() {
            this.submitButtonDisabled = true
            setTimeout(() => {
                this.submitButtonDisabled = false
            }, 1500)
        },
        unvalidateTitle() {
            if (this.title_invalid) {
                if (this.title !== '' && this.title.length < 128) {
                    this.titleClass = 'form-control';
                    this.title_invalid = '';
                }
            }
        },

        unvalidateDescription() {
            if (this.description_invalid) {
                if (this.description !== '') {
                    this.descriptionClass = 'form-control';
                    this.description_invalid = '';
                }
            }
        },

        unvalidateTelegram() {
            if (this.telegram_invalid) {
                if (this.telegram !== '' || this.email !== '') {
                    this.telegramClass = 'form-control';
                    this.telegram_invalid = '';
                }
            }
        },

        unvalidateEmail() {
            if (this.email_invalid) {
                if ((this.telegram !== '' || this.email !== '') && (validEmail(this.email))) {
                    this.emailClass = 'form-control';
                    this.email_invalid = '';
                }
            }
        },

        submitForm() {
            this.titleClass = 'form-control';
            this.descriptionClass = 'form-control';
            this.telegramClass = 'form-control';
            this.emailClass = 'form-control';
            this.alertClass = 'alert mt-5 alert-secondary';

            this.title_invalid = '';
            this.description_invalid = '';
            this.telegram_invalid = '';
            this.email_invalid = '';

            var valid = true;

            if (this.title === '') {
                this.titleClass = 'form-control is-invalid';
                this.title_invalid += 'Заполните тему проблемы.';
                valid = false;
            } else if (this.title.length > 128) {
                this.titleClass = 'form-control is-invalid';
                this.title_invalid += 'Название слишком длинное, поместите лишние данные в описание.';
                valid = false
            }

            if (this.description === '') {
                this.descriptionClass = 'form-control is-invalid';
                this.description_invalid += 'Заполните описание проблемы.';
                valid = false;
            }

            if (this.telegram === '' && this.email === '') {
                this.alertClass = 'alert mt-5 alert-danger';
                this.telegramClass = 'form-control is-invalid';
                this.emailClass = 'form-control is-invalid';
                valid = false;
            } else {
                if (this.email !== '') {
                    if (!validEmail(this.email)) {
                        this.emailClass = 'form-control is-invalid';
                        this.email_invalid = 'Введите корректный email.'
                        valid = false;
                    }
                }
            }

            if (!valid) {
                this.warnDisabled();
                return
            }

            this.loading = true;
            const body = {
                title: this.title,
                description: this.description,
                contact_telegram: this.telegram !== '' ? this.telegram : null,
                contact_email: this.email !== '' ? this.email : null
            };
            let url = `${base_url}/private/api/v1/issues/`
            axios.post(url, body)
                .then(response => {
                    this.loading = false;
                    this.is_done = true;
                })
                .catch(error => {
                    this.loading = false;
                    this.warnDisabled();
                    console.error("There was an error!", error);
                });
        }
    },
    template: `
    <div class="modal-header">
        <h5 class="modal-title" id="staticBackdropSupport">Обращение в службу поддержки</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
    </div>
    <div v-if="!is_done">
        <div class="modal-body">
            <div class="form-floating mb-3">
                <input @keyup="unvalidateTitle()" type="text" :class="titleClass" id="title" v-model="title" name="title">
                <label for="floatingInput">Заголовок</label>
                <div v-if="title_invalid" class="invalid-feedback">[[ title_invalid ]]</div>
            </div>

            <div class="form-floating">
                <textarea @keyup="unvalidateDescription()" :class="descriptionClass" id="description" v-model="description" name="description"
                          style="height: 100px"></textarea>
                <label for="floatingTextarea2">Комментарий</label>
                <div v-if="description_invalid" class="invalid-feedback">[[ description_invalid ]]</div>
            </div>

            <div :class="alertClass" role="alert">
                Заполните хотя бы один контакт, чтобы мы могли с вами связаться:
            </div>

            <div class="form-floating mb-3">
                <input @keyup="unvalidateTelegram()" type="text" :class="telegramClass" id="telegram" v-model="telegram" name="telegram">
                <label for="floatingInput">Telegram</label>
                <div v-if="telegram_invalid" class="invalid-feedback">[[ telegram_invalid ]]</div>
            </div>

            <div class="form-floating mb-3">
                <input @keyup="unvalidateEmail()" type="email" :class="emailClass" id="email" v-model="email" name="email">
                <label for="floatingInput">Email</label>
                <div v-if="email_invalid" class="invalid-feedback">[[ email_invalid ]]</div>
            </div>
        </div>
    </div>
    <div v-if="is_done" class="text-center mt-3 mb-3">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
             class="bi bi-check-circle-fill text-success" viewBox="0 0 16 16">
            <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
        </svg>
        Готово!
    </div>
    <div class="modal-footer" v-if="!is_done">
        <div :class="{ shake: submitButtonDisabled }">
            <button type="button" class="btn btn-secondary" @click="submitForm()">
                <span v-if="loading" class="spinner-border spinner-border-sm" role="status"
                      aria-hidden="true"></span>
                Отправить
            </button>
        </div>
    </div>
    `
}).mount("#issue");
