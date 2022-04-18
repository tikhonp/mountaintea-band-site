const base_url = 'http://127.0.0.1:8000'

function validEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

const app = Vue.createApp({
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
        }
    },
    methods: {
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
                return
            }

            this.loading = true;
            const body = {
                title: this.title,
                description: this.description,
                contact_telegram: this.telegram ? this.telegram !== '' : null,
                contact_email: this.email ? this.email !== '' : null
            };
            axios.post(base_url + "/concerts/issue/", body)
                .then(response => {
                    this.loading = false;
                    this.is_done = true;
                })
                .catch(error => {
                    this.loading = false;
                    console.error("There was an error!", error);
                });
        }
    },
    template: "<div class=\"modal-header\">\n" +
        "                <h5 class=\"modal-title\" id=\"staticBackdropLabel\">Обращение в службу поддержки</h5>\n" +
        "                <button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"modal\" aria-label=\"Close\"></button>\n" +
        "            </div>\n" +
        "            <div v-if=\"!is_done\">\n" +
        "                <div class=\"modal-body\">\n" +
        "                    <div class=\"form-floating mb-3\">\n" +
        "                        <input @keyup=\"unvalidateTitle()\" type=\"text\" :class=\"titleClass\" id=\"title\" v-model=\"title\" name=\"title\">\n" +
        "                        <label for=\"floatingInput\">Заголовок</label>\n" +
        "                        <div v-if=\"title_invalid\" class=\"invalid-feedback\">{{ title_invalid }}</div>\n" +
        "                    </div>\n" +
        "\n" +
        "                    <div class=\"form-floating\">\n" +
        "                        <textarea @keyup=\"unvalidateDescription()\" :class=\"descriptionClass\" id=\"description\" v-model=\"description\" name=\"description\"\n" +
        "                                  style=\"height: 100px\"></textarea>\n" +
        "                        <label for=\"floatingTextarea2\">Комментарий</label>\n" +
        "                        <div v-if=\"description_invalid\" class=\"invalid-feedback\">{{ description_invalid }}</div>\n" +
        "                    </div>\n" +
        "\n" +
        "                    <div :class=\"alertClass\" role=\"alert\">\n" +
        "                        Заполните хотя бы один контакт, чтобы мы могли с вами связаться:\n" +
        "                    </div>\n" +
        "\n" +
        "                    <div class=\"form-floating mb-3\">\n" +
        "                        <input @keyup=\"unvalidateTelegram()\" type=\"text\" :class=\"telegramClass\" id=\"telegram\" v-model=\"telegram\" name=\"telegram\">\n" +
        "                        <label for=\"floatingInput\">Telegram</label>\n" +
        "                        <div v-if=\"telegram_invalid\" class=\"invalid-feedback\">{{ telegram_invalid }}</div>\n" +
        "                    </div>\n" +
        "\n" +
        "                    <div class=\"form-floating mb-3\">\n" +
        "                        <input @keyup=\"unvalidateEmail()\" type=\"email\" :class=\"emailClass\" id=\"email\" v-model=\"email\" name=\"email\">\n" +
        "                        <label for=\"floatingInput\">Email</label>\n" +
        "                        <div v-if=\"email_invalid\" class=\"invalid-feedback\">{{ email_invalid }}</div>\n" +
        "                    </div>\n" +
        "                </div>\n" +
        "            </div>\n" +
        "            <div v-if=\"is_done\" class=\"text-center mt-3\">\n" +
        "                <svg xmlns=\"http://www.w3.org/2000/svg\" width=\"16\" height=\"16\" fill=\"currentColor\"\n" +
        "                     class=\"bi bi-check-circle-fill text-success\" viewBox=\"0 0 16 16\">\n" +
        "                    <path d=\"M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z\"/>\n" +
        "                </svg>\n" +
        "                Готово!\n" +
        "            </div>\n" +
        "            <div class=\"modal-footer\" v-if=\"!is_done\">\n" +
        "                <button type=\"button\" class=\"btn btn-primary\" @click=\"submitForm()\">\n" +
        "                    <span v-if=\"loading\" class=\"spinner-border spinner-border-sm\" role=\"status\"\n" +
        "                          aria-hidden=\"true\"></span>\n" +
        "                    Отправить\n" +
        "                </button>\n" +
        "            </div>"
}).mount("#issue");
