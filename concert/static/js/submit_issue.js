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
                contact_telegram: this.telegram !== '' ? this.telegram : null,
                contact_email: this.email !== '' ? this.email : null
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
    }
}).mount("#issue");
