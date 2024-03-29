var fligtMenu = new Vue({
    el: '#main_flight_menu',
    data: {
        trip_data : {},
        sortParam: '',
        currency : '',
        sortOptions: {'type':'price-low'},
        json:false
        },

    created() {
    },
    mounted() {
    },
    computed:{
        bestFlights: function(){
            if(this.trip_data.flightsArr){
                return this.trip_data.flightsArr.filter((item)=>item.value.notes.indexOf('best') != -1)
            }
            else{
                return []
            }
        },
        lowPriceFlights: function(){
            if(this.trip_data.flightsArr){
                return this.trip_data.flightsArr.filter((item)=>item.value.notes.indexOf('min_price') != -1)
            }
            else{
                return []
            }
        },
        lowTimeFlights: function(){
            if(this.trip_data.flightsArr){
                return this.trip_data.flightsArr.filter((item)=>item.value.notes.indexOf('min_time') != -1)
            }
            else{
                return []
            }
        },
        topPriceFlights: function(){
            if(this.trip_data.flightsArr){
                return this.trip_data.flightsArr.filter((item)=>item.value.notes.indexOf('max_price') != -1)
            }
            else{
                return []
            }
        },
        topTimeFlights: function(){
            if(this.trip_data.flightsArr){
                return this.trip_data.flightsArr.filter((item)=>item.value.notes.indexOf('max_time') != -1)
            }
            else{
                return []
            }
        }
    },
    methods: {
        swapFormat(){
            console.log('swap')
            if(this.json)this.json = false
            else {this.json = true
                    Vue.nextTick(() => {
                        document.getElementById("json_container").innerHTML = JSON.stringify(this.trip_data, undefined, 2);
                    });

            }
        },
        changeSortType(){
            console.log("cur sort type ", this.sortOptions.type )
            this.sortFlights()
        },
        sortFlights(){
            this.trip_data.flightsArr.sort(function(a,b){
                if(this.sortOptions.type == 'price-low'){
                    return b.value.total_price - a.value.total_price
                }
                else if(this.sortOptions.type == 'price-up'){
                    return a.value.total_price - b.value.total_price
                }
                else if(this.sortOptions.type == 'time-low'){
                    return b.value.total_time - a.value.total_time
                }
                else{
                    return a.value.total_time - b.value.total_time
                }
            }.bind(this))
        },
        getTrip(ref){
            this.json = false
            this.trip_data = {};
            from = this.$refs[ref].FROM.value;
            to = this.$refs[ref].TO.value;
            when = this.$refs[ref].WHEN.value;
            when_return = this.$refs[ref].WHEN_RETURN.value;
            who = this.$refs[ref].WHO.value;
            xml = this.$refs[ref].xml.value;
            console.log('cur',this.currency)
            if(this.currency == '' || this.currency == 1){
                local_zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                if(local_zone == null) local_zone = 'Europe/Moscow';
               }

            else{
                local_zone = null;
                }
            var data = new FormData();
            console.log(local_zone);
            data.append('local_zone',local_zone);
            data.append('FROM',from);
            data.append('TO',to);
            data.append('WHEN',when);
            data.append('WHEN_return',when_return);
            data.append('WHO',who);
            data.append('xml',xml);
            $.ajax({
                type: 'POST',
                url: '/get_flight',
                contentType: false,
                data:data,
                processData: false,
                dataType: 'json'
            }).done(function (data) {
                let newData = data.data
                newData.flightsArr = Object.entries(newData.flights).map((item)=>{
                    return {
                        id: item[0],
                        value: item[1]
                    }
                })
                this.trip_data = newData;

            }.bind(this))
                .fail(function (data) {
                alert('reload pls');
                }.bind(this))
         },

    },
    filters:{
        formatData:function(val){
            d = new Date(val)
            return d.toLocaleDateString();
        },
     formatTime: function(val){
               var time = new Date(val*1000);
               var days = time.getUTCDate();
               days -=1
               var hours = time.getUTCHours();
               var minutes = time.getUTCMinutes();
            if(days > 0)
            return (days + 'д ' + hours  + 'ч  ' + minutes + 'мин')
            else return (hours  + 'ч  ' + minutes + 'мин')
            }
    },
    watch: {

    },

    delimiters: ['[[', ']]']
})