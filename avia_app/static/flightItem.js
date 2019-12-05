Vue.component('flight-item', {
    props: ['flightData','currency'],
    data: function () {
      return {

      }
    },
    filters: {
        formatTime: function(val){
            return (val/60/60).toFixed(1) + 'ч.'
        }
    },
    template: `<div class = 'flight-item' >
    <div class = 'flight-item__header'>
         <div class = 'flight-item__id' >id: [[flightData.id]]</div>
         <div class = 'flight-item__notes'>
             <div class = 'flight-item__notes__best'></div>
             <div class = 'flight-item__notes__best'></div>
             <div class = 'flight-item__notes__best'></div>
             <div class = 'flight-item__notes__best'></div>
             <div class = 'flight-item__notes__best'></div>
         </div>
    </div>
    <div class = 'flight-item__content'>
         <div class = 'flight-item__values' >
             <div class = 'flight-item__values__time'>Время: [[flightData.value.total_time | formatTime]]</div>
             <div class = 'flight-item__values__price'>Цена: [[flightData.value.total_price ]][[currency]]</div>
         </div>
         <div class = 'flight-item__info'>
             Информация
         </div>
    </div>
</div>`
    ,
    delimiters: ['[[', ']]']
  })