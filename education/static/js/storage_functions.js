jQuery(document).ready(function ($) {
  $("#trade_tab").on("input", "#cash_at_player", function(){
//  проверка что в форме передачи денег сменились значения
    if($('#cash_at_player').val() !== $('#cash_at_player').attr('value') || $('#cash_at_storage').val() !== $('#cash_at_storage').attr('value') ){
        $("#do_transfer").attr("disabled", false);
    }
    else{
        $("#do_transfer").attr("disabled", true);
    }
//    если в одном поле увеличилось значние, надо уменьшить в другом и наоборот
    $('#cash_at_storage').val(parseInt(document.getElementById('cash').dataset.text) + parseInt(document.getElementById('storage_cash').dataset.text) - $('#cash_at_player').val() );
  });

  $("#trade_tab").on("input", "#cash_at_storage", function(){
//  проверка что в форме передачи денег сменились значения
    if($('#cash_at_player').val() !== $('#cash_at_player').attr('value') || $('#cash_at_storage').val() !== $('#cash_at_storage').attr('value') ){
        $("#do_transfer").attr("disabled", false);
    }
    else{
        $("#do_transfer").attr("disabled", true);
    }
//    если в одном поле увеличилось значние, надо уменьшить в другом и наоборот
    $('#cash_at_player').val(parseInt(document.getElementById('cash').dataset.text) + parseInt(document.getElementById('storage_cash').dataset.text) - $('#cash_at_storage').val() );
  });

//  подсказка стоимости энергетиков в золоте
    $("#trade_tab").on("input", "#batteries_count", function(){
        document.getElementById('recharge_cost').innerHTML = "- " + Math.ceil(document.getElementById('batteries_count').value/10) + " G";
    });

//  при передаче денег
    $("#trade_tab").on("submit", "#money_transfer_frm", function(e){
        e.preventDefault();

        if (launched !== true){

//      --количество--
            for (let i = 0; i < 800; i++) {
              setTimeout(() => {
                $('#cash_at_storage').val($('#cash_at_storage').val() - 1)
                $('#cash_at_player').val(parseInt($('#cash_at_player').val()) + 1);
                $('#cash').html(numberWithSpaces(parseInt($('#cash_at_player').val()) + 1));
              }, i * 1); // 10 миллисекунд = 0.01 секунда
            }

            claim_reward('cash');
            launched = true;
        }
    });

});