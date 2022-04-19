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
                    this.$refs.submit.click();
                })
                .catch((error) => {
                    this.pay_loading = false;
                    this.fetchInitData();
                    this.error = error.response.data.error;
                    console.log(error);
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
                // Editing in the middle of input, not last symbol
                if (e.data && /\D/g.test(e.data)) {
                    // Attempt to input non-numeric symbol
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
            // Clear input after remove last symbol
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
}).mount("#app");
