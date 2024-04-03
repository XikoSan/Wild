function loadCssVariablesFromLocalStorage() {
  const cssVariables = JSON.parse(localStorage.getItem('cssVariables'));

  if (cssVariables) {
    for (const variable in cssVariables) {
      document.documentElement.style.setProperty(variable, cssVariables[variable]);
    }
  }
}

loadCssVariablesFromLocalStorage();
