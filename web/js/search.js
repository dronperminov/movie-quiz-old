function ClearQuery() {
    let queryInput = document.getElementById("query")
    let clearIcon = document.getElementById("clear-icon")

    queryInput.value = ""
    clearIcon.classList.add("clear-hide")
}

function QueryInput(e) {
    let queryInput = document.getElementById("query")
    let clearIcon = document.getElementById("clear-icon")

    if (queryInput.value != "")
        clearIcon.classList.remove("clear-hide")
    else
        clearIcon.classList.add("clear-hide")
}

function QueryKeyDown(e, onEnter) {
    if (e.key == "Enter")
        onEnter()
}
