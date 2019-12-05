Vue.component('flight-item', {
    props: ['flightData','currency'],
    data: function () {
      return {

      }
    },
    filters: {
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
             <div class = 'flight-item__values__time'>Время полета: [[flightData.value.total_time | formatTime]]</div>
             <div class = 'flight-item__values__price'>Цена: &nbsp; [[flightData.value.total_price ]][[currency]]</div>
         </div>
         <div class = 'flight-item__info'>
             Информация (выводится при необходимости)
         </div>
    </div>
</div>`
    ,
    delimiters: ['[[', ']]']
  })