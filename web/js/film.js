const REMOVE_ICON = `<svg class="form-svg-fill-icon" width="20px" height="20px" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 4h3c.6 0 1 .4 1 1v1H3V5c0-.6.5-1 1-1h3c.2-1.1 1.3-2 2.5-2s2.3.9 2.5 2zM8 4h3c-.2-.6-.9-1-1.5-1S8.2 3.4 8 4zM4 7h11l-.9 10.1c0 .5-.5.9-1 .9H5.9c-.5 0-.9-.4-1-.9L4 7z"/>
</svg>`

function GetFactBlock(factBlock) {
    while (!factBlock.classList.contains("fact-block"))
        factBlock = factBlock.parentNode

    return factBlock
}

function ChangeFact(block) {
    let factBlock = GetFactBlock(block)
    let icon = factBlock.getElementsByClassName("form-row-icon-interactive")[0]
    let error = document.getElementById("error")

    factBlock.classList.remove("error-input")
    icon.classList.remove("error-icon")
    error.innerText = ""

    ShowSaveButton()
}

function RemoveFact(factIcon) {
    ChangeFact(factIcon)

    let factsBlock = document.getElementById("facts")
    let block = GetFactBlock(factIcon)
    let index = 0

    while (factsBlock.children[index] != block)
        index++

    block.remove()
    markups.splice(index, 1)
}

function AddFact() {
    let factsBlock = document.getElementById("facts")

    let factBlock = MakeElement("form-row fact-block", factsBlock)
    let block = MakeElement("table-block table-block-no-spacing fact", factBlock)
    let inputCell = MakeElement("table-cell", block)
    let factArea = MakeElement("fact-area", inputCell)
    let factInputHighlight = MakeElement("fact-input-highlight", factArea)
    let factInput = MakeElement("basic-textarea default-textarea fact-input", factArea, {tag: "textarea"})
    factInput.addEventListener("input", () => ChangeFact(factBlock))

    let spoilerBlock = MakeElement("fact-spoiler", inputCell)
    let label = MakeElement("", spoilerBlock, {tag: "label"})
    let spoiler = MakeElement("", label, {tag: "input", type: "checkbox"})
    let span = MakeElement("", label, {tag: "span", innerText: "Спойлер"})
    spoiler.addEventListener("change", () => ChangeFact(factBlock))

    let iconCell = MakeElement("table-cell table-cell-no-width form-row-top-icon", block)
    let icon = MakeElement("form-row-icon-interactive", iconCell, {title: "Удалить", innerHTML: REMOVE_ICON})
    icon.addEventListener("click", () => RemoveFact(icon))

    ChangeFact(factBlock)
    markups.push(new Markup(factInput, factInputHighlight, [], () => ChangeFact(factBlock)))
}

function GetFacts() {
    let factsBlock = document.getElementById("facts")
    let error = document.getElementById("error")
    let facts = []
    error.innerText = ""

    for (let i = 0; i < factsBlock.children.length; i++) {
        let factBlock = factsBlock.children[i]
        let factInput = factBlock.getElementsByTagName("textarea")[0]
        let factIcon = factBlock.getElementsByClassName("form-row-icon-interactive")[0]
        let spoilerInput = factBlock.getElementsByTagName("input")[0]
        let value = factInput.value
        let spans = markups[i].GetSpans()
        let spoiler = spoilerInput.checked

        if (value.trim() === "") {
            error.innerText = "Факт пустой"
            factIcon.classList.add("error-icon")
            factBlock.classList.add("error-input")
            factBlock.scrollIntoView({behaviour: "smooth"})
            return null
        }

        factBlock.classList.remove("error-input")
        factIcon.classList.remove("error-icon")
        facts.push({value: value, spans: spans, spoiler: spoiler})
    }

    return facts
}

function SaveFilm() {
    let name = GetTextField("name", "Название не заполнено")
    if (name === null)
        return

    let movie_type = document.getElementById("movie-type").value

    let year = GetNumberField("year", /^\d\d\d\d$/g, "Год выхода введён неверно")
    if (year === null)
        return

    let slogan = GetTextField("slogan")
    if (slogan === null)
        return

    let descriptionValue = GetTextField("description")
    let description = {value: descriptionValue, spans: descriptionMarkup.GetSpans()}
    if (descriptionValue === null)
        return

    let shortDescriptionValue = GetTextField("short-description")
    if (shortDescriptionValue === null)
        return
    let short_description = {value: shortDescriptionValue, spans: shortDescriptionMarkup.GetSpans()}

    let countries = GetTextListField("countries", "Страна выхода не указана")
    if (countries === null)
        return

    let genres = GetTextListField("genres", "Жанр не указан")
    if (genres === null)
        return

    let length = GetNumberField("length")
    let tops = GetMultiSelect("top-lists", null)

    let facts = GetFacts()
    if (facts === null)
        return

    let film = document.getElementById("film")
    let film_id = film.getAttribute("data-film-id")

    let button = document.getElementById("save-btn")
    let edited = document.getElementById("edited")
    let error = document.getElementById("error")
    error.innerText = ""

    SendRequest("/update-film", {film_id, name, movie_type, year, slogan, description, short_description, countries, genres, length, tops, facts}).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return
        }

        button.classList.add("hidden")

        if (response.edited)
            edited.classList.remove("hidden")
    })
}

function RemoveFilm() {
    if (!confirm("Вы уверены, что хотите удалить этот фильм?"))
        return

    let film = document.getElementById("film")
    let filmId = +film.getAttribute("data-film-id")
    let error = document.getElementById("error")
    error.innerText = ""

    SendRequest("/remove-film", {film_id: filmId}).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return
        }

        window.location = "/films"
    })
}
