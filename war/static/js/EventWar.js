jQuery(document).ready(function ($) {

    $(".war__units-count").on("input", ".unit_input", function(e){

        var energy_count = Number(0);
        var units_count = 0;
        var damage_count = 0;

        $('.unit_input').each(function(i, obj) {
            units_count += Number(obj.value);
            energy_count += units_energy[obj.id] * obj.value;
            damage_count += Math.floor( (units_damage[obj.id] * obj.value) * (1 + player_pwr/100) * units_mod[obj.id]);
        });

        $('#energy_count' ).html( energy_count );
        $('#damage_count' ).html( damage_count );
    });
});
