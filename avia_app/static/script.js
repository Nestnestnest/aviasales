var fligtMenu = new Vue({
    el: '#main_flight_menu',
    data: {
        trip_data : {},
        sortParam: '',
        currency : '',
        },

    created() {
    },
    mounted() {
    },
    methods: {
        getTrip(ref){

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
                console.log('data', data)
                this.trip_data = data.data;
            }.bind(this))
                .fail(function (data) {
                    console.log('fail');
                })
         },

    },
    filters:{
        formatData:function(val){
            d = new Date(val)
            return d.toLocaleDateString();
        }
    },

    delimiters: ['[[', ']]']
})