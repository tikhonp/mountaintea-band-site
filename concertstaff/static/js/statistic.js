const app = Vue.createApp({
    delimiters: ['[[',']]'],
    data() {
        return {
            tickets: null,
            amount_sum: null,
            tickets_sum: null,
            entered_percent: null,
            concert: null,
            user: null,

            data_loading: true,
            search_loading: false,
            submitButtonDisabled: false,
            is_search: false,

            error: '',
            query: '',
            base_url: base_url,
        }
    },
    methods: {
        warnDisabled() {
            this.submitButtonDisabled = true
            setTimeout(() => {
                this.submitButtonDisabled = false
            }, 1500)
        },
        search() {
            if (this.query === '') {
                this.warnDisabled();
            } else {
                this.search_loading = true;
                this.is_search = true
                this.fetchInitData(this.query);
            }
        },
        fetchInitData(query) {
            axios.get(base_url + window.location.pathname + 'data/', {
                withCredentials: true,
                params: { query: query }
            })
                .then((response) => {
                    this.tickets = response.data.tickets;
                    this.amount_sum = response.data.amount_sum;
                    this.tickets_sum = response.data.tickets_sum;
                    this.entered_percent = response.data.entered_percent;
                    this.concert = response.data.concert;
                    this.user = response.data.user;

                    this.data_loading = false;
                    this.search_loading = false;
                })
                .catch((error) => {
                    this.error = 'Упс! Что-то не работает, пожалуйста, сообщите нам.';
                    this.search_loading = false;
                    console.log(error);
                })
        }
    },
    mounted() {
        this.fetchInitData('');
    },
    template: `
    <div v-if="data_loading" class="d-flex justify-content-center align-middle my-5">
        <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>
    
    <div v-if="error && data_loading" class="alert alert-danger" role="alert">
        [[ error ]]
    </div>
    
    <div v-if="!data_loading">
        <nav class="navbar navbar-light justify-content-center">
            <div class="container-fluid">
                <a class="navbar-brand" href="/staff/">MountainTea</a>
                <span class="navbar-text">[[ concert.title ]]</span>
                <div class="d-flex" v-if="tickets_sum != 0 || is_search">
                    <input class="form-control me-2" type="text" placeholder="Поиск билета" aria-label="Search"
                           v-model="query">
                    <div :class="{ shake: submitButtonDisabled }">
                        <button class="btn btn-outline-secondary" type="button" @click="search">
                            <span v-if="search_loading" class="spinner-border spinner-border-sm" role="status"
                                aria-hidden="true"></span> Найти
                        </button>
                    </div>
                </div>
            </div>
        </nav>
        
        <div v-if="error" class="alert alert-danger" role="alert">
            [[ error ]]
        </div>
           
        <div v-if="tickets_sum != 0">
            <div class="alert alert-secondary" role="alert">
                Всего собрано
                <mark>[[ amount_sum.toFixed(2) ]]</mark>
                рублей. Куплено билетов -
                <mark>[[ tickets_sum ]]</mark>
                <small class="pb-2">(С учетом коммисии 2%)</small>
            </div>

            <div v-if="entered_percent != 0">
                <h5>Прогресс посещения мероприятия</h5>

                <div class="progress mt-3 mb-3" style="height: 20px;">
                    <div class="progress-bar" role="progressbar" style="width: [[ entered_percent ]]%;"
                         aria-valuenow="[[ entered_percent ]]" aria-valuemin="0"
                         aria-valuemax="100">[[ entered_percent ]]%
                    </div>
                </div>
            </div>

            <table class="table table-hover table-sm caption-top">
                <caption>Билеты</caption>
                <thead>
                <tr>
                    <th scope="col">Номер билета</th>
                    <th scope="col">Дата создания</th>
                    <th scope="col">Имя и Фамилия</th>
                    <th scope="col">Активен</th>
                    <th scope="col">Цена билета</th>
                </tr>
                </thead>
                <tbody>
                    <tr v-for="i in tickets">
                        <th scope="row">
                            <a :href="'/staff/submit/' + i.number + '/' + i.get_hash + '/'" class="link-dark">
                                [[ i.number ]]</a>
                        </th>
                        <td>[[ i.transaction.date_created ]]</td>
                        <td>
                            <div v-if="user.is_superuser">
                                <a :href="'/admin/auth/user/' + i.transaction.user.pk + '/change/'" class="link-dark">
                                    [[ i.transaction.user.first_name ]]</a>
                            </div>
                            <div v-else>
                                [[ i.transaction.user.first_name ]]
                            </div>
                        </td>
                        <td>
                            <div v-if="i.is_active">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                     class="bi bi-check-circle-fill" viewBox="0 0 16 16">
                                    <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"></path>
                                </svg>
                            </div>
                            <div v-else>
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                                     class="bi bi-x-circle-fill" viewBox="0 0 16 16">
                                    <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path>
                                </svg>
                            </div>
                        </td>
                        <td>
                            <div v-if="user.is_superuser">
                                <a :href="'/admin/concert/price/' + i.price.id + '/change/'" class="link-dark">
                                    [[ i.price.price.toFixed(2) ]]</a>
                            </div>
                            <div v-else>
                                [[ i.price.price.toFixed(2) ]]
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div v-if="tickets_sum == 0" class="alert alert-info" role="alert">
            <div v-if="is_search">
                К сожалению, ничего не нашлось...
            </div>
            <div v-else>
                Еще не куплено ни одного билета на этот концерт.
            </div>
        </div>
    </div>
    `
}).mount("#stat");
