jQuery(document).ready(function ($) {
// отправить законопроект на рассмотрение
    $('.new_bill').submit(function(e){
        e.preventDefault();

        var sending_data = new FormData(this);
        sending_data.append('bill_type', current_bill);
        sending_data.append('construction_regions', document.getElementById('construction_default_region').dataset.value);
        sending_data.append('explore_regions', document.getElementById('explore_resources_default_region').dataset.value);
        sending_data.append('independence_regions', document.getElementById('independence_default_region').dataset.value);

        $.ajax({
              url: "/new_bill/",
              type: "POST",
              data: sending_data,
              processData: false,  // Сообщить jQuery не передавать эти данные
              contentType: false,   // Сообщить jQuery не передавать тип контента
              success: function(result){
                  if (result.response == 'ok'){
                      location.reload();
                  }
                  else{
                      display_modal('notify', result.header, result.response, null, result.grey_btn)
                  }
            }
        });
    });
});