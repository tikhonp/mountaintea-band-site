window.addEventListener("load", function(_event) {
    const app = Vue.createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                tickets: [],
                amount_sum: 0,
                tickets_sum: null,
                entered_percent: null,
                concert: null,
                user: null,

                data_loading: true,
                search_loading: false,
                submitButtonDisabled: false,
                is_search: false,
                tickets_finished_loading: false,

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
                    this.loadTickets(this.query);
                }
            },
            updateLoadingStatus() {
                if (this.user !== null && this.tickets_finished_loading && this.concert !== null) {
                    this.data_loading = false;
                    this.search_loading = false;
                }
            },
            loadTickets(query) {
                let tickets_url = `${base_url}/private/api/v1/tickets/`
                axios.get(tickets_url, {
                    withCredentials: true, params: {
                        search: query,
                        transaction__is_done: true,
                        transaction__concert: concert_id,
                        ordering: '-transaction__date_created'
                    }
                })
                    .then((response) => {
                        this.tickets = response.data

                        this.amount_sum = this.c_amount_sum()
                        this.tickets_sum = this.c_tickets_sum()
                        this.entered_percent = this.c_entered_percent()

                        this.tickets_finished_loading = true
                        this.updateLoadingStatus();
                    })
                    .catch((error) => {
                        this.error = 'Упс! Что-то не работает, пожалуйста, сообщите нам.';
                        this.search_loading = false;
                        console.log(error);
                    })
            },
            printDateTime(dateTimeString) {
                let now = new Date()
                let date = new Date(dateTimeString)

                let isToday = date.getDate() === now.getDate() &&
                    date.getMonth() === now.getMonth() &&
                    date.getFullYear() === now.getFullYear()

                if (isToday) {
                    return `Сегодня в ${date.toLocaleString(undefined, {
                        timeStyle: "short",
                    })}`
                } else if (date.getFullYear() === now.getFullYear()) {
                    return date.toLocaleString(undefined, {
                        day: "numeric",
                        month: "long",
                        hour: "2-digit",
                        minute: "2-digit",
                    })
                } else {
                    return date.toLocaleString(undefined, {
                        day: "numeric",
                        month: "long",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                    })
                }
            },
            fetchInitData() {
                this.loadTickets('');

                let concert_url = `${base_url}/private/api/v1/concerts/${concert_id}/`
                axios.get(concert_url, { withCredentials: true })
                    .then((response) => {
                        this.concert = response.data
                        this.updateLoadingStatus();
                    })
                    .catch((error) => {
                        this.error = 'Упс! Что-то не работает, пожалуйста, сообщите нам.';
                        this.search_loading = false;
                        console.log(error);
                    })

                let user_url = `${base_url}/private/api/v1/user/`
                axios.get(user_url, { withCredentials: true })
                    .then((response) => {
                        this.user = response.data;
                        this.updateLoadingStatus();
                    })
                    .catch((error) => {
                        this.error = 'Упс! Что-то не работает, пожалуйста, сообщите нам.';
                        this.search_loading = false;
                        console.log(error);
                    })
            },
            c_amount_sum() {
                let sum = 0;
                let transaction = [];
                for (let t in this.tickets) {
                    if (!transaction.includes(this.tickets[t].transaction.id)) {
                        sum += this.tickets[t].transaction.amount_sum;
                        transaction.push(this.tickets[t].transaction.id);
                    }
                }
                return sum;
            },
            c_tickets_sum() {
                return this.tickets.length;
            },
            c_entered_percent() {
                if (this.tickets_sum == 0) {
                    return 0;
                }
                let not_active_tickets = this.tickets.filter(t => !t.is_active).length
                let entered = not_active_tickets / this.tickets_sum;
                return Number(entered * 100)
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
                           v-model="query" v-on:keyup.enter="search">
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
                рублей. <small class="pb-2">(С учетом коммисии)</small>
                Куплено билетов: <mark>[[ tickets_sum ]]</mark>
            </div>

            <div v-if="entered_percent != 0">
                <h5>Прогресс посещения мероприятия</h5>

                <div class="progress mt-3 mb-3" style="height: 20px;">
                    <div class="progress-bar" role="progressbar" :style="'width: ' + entered_percent + '%;'"
                         :aria-valuenow="entered_percent" aria-valuemin="0"
                         aria-valuemax="100">[[ Math.trunc(entered_percent) ]]%
                    </div>
                </div>
            </div>
            
            <div class="table-responsive">
                <table class="table table-hover table-sm caption-top">
                    <caption>Билеты</caption>
                    <thead>
                    <tr>
                        <th scope="col">Номер билета</th>
                        <th scope="col">Дата создания</th>
                        <th scope="col">Имя и Фамилия</th>
                        <th scope="col">Статус</th>
                        <th scope="col">Цена билета</th>
                    </tr>
                    </thead>
                    <tbody>
                        <tr v-for="i in tickets">
                            <th scope="row">
                                <a :href="'/staff/submit/' + i.number + '/' + i.hash + '/'" class="link-dark">
                                    [[ i.number ]]</a>
                            </th>
                            <td>[[ printDateTime(i.transaction.date_created) ]]</td>
                            <td>
                                <div v-if="user.is_superuser">
                                    <a :href="'/admin/auth/user/' + i.transaction.user.id + '/change/'" class="link-dark">
                                        [[ i.transaction.user.first_name ]]</a>
                                </div>
                                <div v-else>
                                    [[ i.transaction.user.first_name ]]
                                </div>
                            </td>
                            <td>
                                <i v-if="i.is_active" class="fa-solid fa-check text-success me-2"> </i> 
                                <i v-else class="fa-solid fa-xmark text-danger me-2"> </i> 
                                <i v-if="i.transaction.email_status === 'delivered'" 
                                   class="fa-solid fa-envelope-circle-check text-success"> </i> 
                                <i v-if="i.transaction.email_status === 'opened'" class="fa-solid fa-envelope-open text-success"> </i> 
                                <i v-if="i.transaction.email_status === 'accepted' || i.transaction.email_status === 'unnecessary'" 
                                    class="fa-solid fa-envelope text-warning"> </i> 
                                <i v-if="i.transaction.email_status === 'rejected' || i.transaction.email_status === 'failed'" 
                                   class="fa-solid fa-envelope text-danger"> </i> 
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
});
