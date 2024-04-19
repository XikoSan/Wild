jQuery(document).ready(function ($) {
// отправить законопроект на рассмотрение
    $('.new_bill').submit(function(e){
        e.preventDefault();

        var sending_data = new FormData(this);
        sending_data.append('bill_type', current_bill);
        sending_data.append('construction_regions', document.getElementById('construction_default_region').dataset.value);
        sending_data.append('explore_regions', document.getElementById('explore_resources_default_region').dataset.value);
        sending_data.append('change_taxes_regions', document.getElementById('change_taxes_default_region').dataset.value);

        var trans_default = document.getElementById('transfer_region_default_region');
        if (trans_default) {
            sending_data.append('transfer_region_regions', trans_default.dataset.value);
        }

        var trans_state_default = document.getElementById('transfer_region_default_state');
        if (trans_state_default) {
            sending_data.append('transfer_region_states', trans_state_default.dataset.value);
        }

        var ind_default = document.getElementById('independence_default_region');
        if (ind_default) {
            sending_data.append('independence_regions', ind_default.dataset.value);
        }

        var agr_default = document.getElementById('start_war_default_region');
        if (agr_default) {
            sending_data.append('war_region_from', agr_default.dataset.value);
        }

        var def_default = document.getElementById('start_war_default_victim');
        if (def_default) {
            sending_data.append('war_region_to', def_default.dataset.value);
        }

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