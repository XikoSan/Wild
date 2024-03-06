jQuery(document).ready(function ($) {

    $(".war__units-count").on("input", ".unit_input", function(e){

        var energy_count = Number(0);
        var units_count = 0;
        var damage_count = 0;
        var units_dmg = 0;

        var total_units = 0;
        var bonus = 0.0;
        var types_count = 0;

        if (coherence_perk == true){
            $('.unit_input').each(function(i, obj) {
                total_units += Number(obj.value);
            });
            $('.unit_input').each(function(i, obj) {
                if (Number(obj.value) * 100 / total_units >= 20){
                    types_count += 1;
                    bonus += 0.1;
                }
            });
        }

        $('.unit_input').each(function(i, obj) {
            units_count += Number(obj.value);
            energy_count += units_energy[obj.id] * obj.value;

            units_dmg = Math.floor( (units_damage[obj.id] * obj.value) * (1 + player_pwr/100) );

            if (scouting_perk > 0 ){
                units_dmg = Math.floor( units_dmg * (1 + scouting_perk * 0.02) );
            }

            if (coherence_perk == true && types_count > 1){
                units_dmg = Math.floor( units_dmg * (1 + bonus) );
            }

            damage_count += Math.floor( units_dmg * units_mod[obj.id]);
        });

        $('#energy_count' ).html( energy_count );
        $('#damage_count' ).html( damage_count );
    });
});
