const app = Vue.createApp({
    delimiters: ['[[',']]'],
    data() {
        return {
            data_loading: true,
            pay_loading: false,

            concert: {},
            prices: [],

            name: '',
            email: '',
            phone: '',

            nameFocused: false,
            emailFocused: false,
            phoneFocused: false,

            transaction_id: null,

            nameInvalid: false,
            emailInvalid: false,
            phoneInvalid: false,
            amountInvalid: false,

            error: '',
        }
    },
    methods: {
        submitForm() {
            this.pay_loading = true;

            this.nameInvalid = !this.isNameValid;
            this.emailInvalid = !this.isEmailValid;
            this.phoneInvalid = !this.isPhoneValid;
            this.amountInvalid = !(this.amount > 0);

            if (this.nameInvalid || this.emailInvalid || this.phoneInvalid || this.amountInvalid) {
                this.pay_loading = false;
                return
            }

            const data = {
                user: {
                    name: this.name,
                    email: this.email,
                    phone_number: this.phone
                },
                tickets: Object.fromEntries(this.prices.map( x => [x.id, x.count]))
            }
            axios.post(base_url + window.location.pathname, data)
                .then((response) => {
                    this.transaction_id = response.data.transaction_id
                    this.pay_loading = false;
                })
                .catch((error) => {
                    this.pay_loading = false;
                    this.fetchInitData();
                    this.error = error.response.data.error;
                    console.log(error);
                })
                .then(() => {
                    if (this.transaction_id != null) {
                        this.$refs.submit.click();
                    }
                });
        },
        formatPrice(value) {
            return value.toFixed(2).toLocaleString();
        },
        incrementPrice(indx) {
            this.prices[indx].count = this.prices[indx].count + 1;
        },
        decrementPrice(indx) {
            if (this.prices[indx].count !== 0) {
                this.prices[indx].count = this.prices[indx].count - 1;
            }
        },
        onPhonePaste(e) {
            let input = e.target,
            inputNumbersValue = this.getInputNumbersValue(input);
            var pasted = e.clipboardData || window.clipboardData;
            if (pasted) {
                var pastedText = pasted.getData('Text');
                if (/\D/g.test(pastedText)) {
                    input.value = inputNumbersValue;
                    return;
                }
            }
        },
        onPhoneInput(e) {
            var input = e.target,
                inputNumbersValue = this.getInputNumbersValue(input),
                selectionStart = input.selectionStart,
                formattedInputValue = "";

            if (!inputNumbersValue) {
                return input.value = "";
            }

            if (input.value.length != selectionStart) {
                if (e.data && /\D/g.test(e.data)) {
                    input.value = inputNumbersValue;
                }
                return;
            }

            if (["7", "8", "9"].indexOf(inputNumbersValue[0]) > -1) {
                if (inputNumbersValue[0] == "9") inputNumbersValue = "7" + inputNumbersValue;
                var firstSymbols = (inputNumbersValue[0] == "8") ? "8" : "+7";
                formattedInputValue = input.value = firstSymbols + " ";
                if (inputNumbersValue.length > 1) {
                    formattedInputValue += '(' + inputNumbersValue.substring(1, 4);
                }
                if (inputNumbersValue.length >= 5) {
                    formattedInputValue += ') ' + inputNumbersValue.substring(4, 7);
                }
                if (inputNumbersValue.length >= 8) {
                    formattedInputValue += '-' + inputNumbersValue.substring(7, 9);
                }
                if (inputNumbersValue.length >= 10) {
                    formattedInputValue += '-' + inputNumbersValue.substring(9, 11);
                }
            } else {
                formattedInputValue = '+' + inputNumbersValue.substring(0, 16);
            }
            input.value = formattedInputValue;
        },
        onPhoneKeyDown(e) {
            var inputValue = e.target.value.replace(/\D/g, '');
            if (e.keyCode == 8 && inputValue.length == 1) {
                e.target.value = "";
            }
        },
        getInputNumbersValue(input) {
            return input.value.replace(/\D/g, '');
        },
        fetchInitData() {
            axios.get(base_url + window.location.pathname + 'data/')
            .then((response) => {
                this.concert = response.data.concert;
                this.prices = response.data.prices;
                this.data_loading = false;
            })
            .catch(function (error) {
                console.log(error);
            })
        }
    },
    computed: {
        isEmailValid() {
            var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            return re.test(this.email);
        },
        isNameValid() {
            return (this.name.length < 150 && this.name !== '');
        },
        isPhoneValid() {
            return this.phone !== '';
        },
        amount() {
            var amount = 0;
            for (let price of this.prices) {
                amount += price.price * price.count;
            }
            return amount;
        },
    },
    mounted() {
        this.fetchInitData();
    },
    template: `
    <div v-if="data_loading" class="d-flex justify-content-center align-middle my-5">
        <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>

    <div v-if="!data_loading && prices" class="mt-2 mb-4">
        <div class="">

            <h2>Билет на концерт - [[ concert.title ]]</h2>
            <p>Когда: [[ concert.date_time ]].</p>

            <div v-if="prices.length == 0">
                <div class="alert alert-info" role="alert">
                    К сожалению, билеты закончились.
                </div>

                <div v-if="error" class="alert alert-danger" role="alert">
                    [[ error ]]
                </div>
            </div>

            <div v-if="prices.length != 0">
                <div v-if="concert.buy_ticket_message" class="alert alert-info" role="alert">
                    [[ concert.buy_ticket_message ]]
                </div>

                <div class="form-floating mb-3" :class="{'shadow': nameFocused}">
                    <input id="floatingInputn" type="text" class="form-control" v-model="name"
                           @focus="nameFocused = true" @blur="nameFocused = false" required
                           :class="{'is-invalid': nameInvalid}">
                    <label for="floatingInputn">Имя и Фамилия</label>
                </div>

                <div class="form-floating mb-3" :class="{'shadow': emailFocused}">
                    <input type="email" class="form-control" id="floatingInpute" v-model="email" required
                           @focus="emailFocused = true" @blur="emailFocused = false"
                           :class="{'is-invalid': emailInvalid}">
                    <label for="floatingInpute">Электронная почта</label>
                </div>

                <div class="form-floating mb-3" :class="{'shadow': phoneFocused}">
                    <input maxlength="18" type="tel" @keydown="onPhoneKeyDown" @input="onPhoneInput"
                           @paste="onPhonePaste" @focus="phoneFocused = true" @blur="phoneFocused = false"
                           class="form-control" id="id_phone_number" v-model="phone" required
                           :class="{'is-invalid': phoneInvalid}"/>
                    <label for="id_phone_number">Номер телефона</label>
                </div>

                <div class="row">
                    <div v-for="(price, index) in prices" :key="price.id">
                        <div class="col">
                            <div class="card mb-3">
                                <div class="card-body">
                                    <h6 class="card-subtitle mb-2 text-muted">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-ticket-perforated-fill" viewBox="0 0 16 16">
                                          <path d="M0 4.5A1.5 1.5 0 0 1 1.5 3h13A1.5 1.5 0 0 1 16 4.5V6a.5.5 0 0 1-.5.5 1.5 1.5 0 0 0 0 3 .5.5 0 0 1 .5.5v1.5a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 0 11.5V10a.5.5 0 0 1 .5-.5 1.5 1.5 0 1 0 0-3A.5.5 0 0 1 0 6V4.5Zm4-1v1h1v-1H4Zm1 3v-1H4v1h1Zm7 0v-1h-1v1h1Zm-1-2h1v-1h-1v1Zm-6 3H4v1h1v-1Zm7 1v-1h-1v1h1Zm-7 1H4v1h1v-1Zm7 1v-1h-1v1h1Zm-8 1v1h1v-1H4Zm7 1h1v-1h-1v1Z"/>
                                        </svg> [[ price.description ]]
                                    </h6>
                                    <p class="card-text">[[ formatPrice(price.price) ]] [[
                                        price.currency ]]</p>
                                    <div class="row mb-3">
                                        <div class="row">
                                            <div class="col text-end">
                                                <button type="button" class="btn btn-secondary"
                                                        @click="decrementPrice(index);">-
                                                </button>
                                            </div>
                                            <div class="col">
                                                <input class="form-control rounded" type="text" type="number" min="0"
                                                       v-model="price.count" :key="index"/>
                                            </div>
                                            <div class="col">
                                                <button type="button" class="btn btn-secondary"
                                                        @click="incrementPrice(index);">+
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-if="amount" class="card mb-2">
                    <div class="card-body">
                        Сумма: [[ amount ]] руб.
                    </div>
                </div>

                <div v-if="amountInvalid && !amount" class="alert alert-danger" role="alert">
                    Добавьте хотя бы один билет.
                </div>

                <div v-if="error" class="alert alert-danger" role="alert">
                    [[ error ]]
                </div>

                <div class="d-grid gap-2 mt-3">
                    <button class="btn btn-secondary btn-lg" type="button" @click="submitForm">
                    <span v-if="pay_loading" class="spinner-border spinner-border-sm" role="status"
                      aria-hidden="true"></span>
                         <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-credit-card" viewBox="0 0 16 16">
                          <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm2-1a1 1 0 0 0-1 1v1h14V4a1 1 0 0 0-1-1H2zm13 4H1v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V7z"/>
                          <path d="M2 10a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-1z"/>
                        </svg> оплатить
                    </button>
                </div>

                <form method="POST" action="https://yoomoney.ru/quickpay/confirm.xml">
                    <input type="hidden" name="successURL"
                           :value="'https://mountainteaband.ru/concerts/tickets/donepayment/?t=' + transaction_id"/>
                    <input type="hidden" name="receiver" :value="concert.yandex_wallet_receiver"/>
                    <input type="hidden" name="formcomment" :value="'Горный Чай: ' + concert.title"/>
                    <input type="hidden" name="short-dest" :value="'Горный Чай: ' + concert.title"/>
                    <input type="hidden" name="label" :value="transaction_id"/>
                    <input type="hidden" name="quickpay-form" value="shop"/>
                    <input type="hidden" name="targets" :value="'Горный Чай: ' + concert.title"/>
                    <input type="hidden" name="sum" :value="amount" data-type="number"/>
                    <input type="hidden" name="paymentType" value="AC"/>
                    <button ref="submit" style="display:none;" type="submit"></button>
                </form>

            </div>
        </div>
    </div>
    `
}).mount("#app");
