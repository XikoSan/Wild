function up_skill(button, skill) {
    // Скрываем нажатую кнопку
    button.style.display = "none";

    // Находим и показываем кнопку с id "skill_" + аргумент функции
    const skillButton = document.getElementById("skill_" + skill);
    if (skillButton) {
        skillButton.style.display = "flex"; // или "block" по вашему желанию
    }

    claim_reward(skill);
}