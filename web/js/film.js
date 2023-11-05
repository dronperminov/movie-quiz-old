const REMOVE_ICON = `<svg class="form-svg-fill-icon" width="20px" height="20px" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 4h3c.6 0 1 .4 1 1v1H3V5c0-.6.5-1 1-1h3c.2-1.1 1.3-2 2.5-2s2.3.9 2.5 2zM8 4h3c-.2-.6-.9-1-1.5-1S8.2 3.4 8 4zM4 7h11l-.9 10.1c0 .5-.5.9-1 .9H5.9c-.5 0-.9-.4-1-.9L4 7z"/>
</svg>`

function ClearBannerError() {
    let urlInput = document.getElementById("banner-url")
    let error = document.getElementById("banner-error")

    urlInput.classList.remove("error-input")
    error.innerText = ""
}

function UpdateBanner(filmId) {
    let banner = document.getElementById("banner")
    let urlInput = document.getElementById("banner-url")
    let url = urlInput.value.trim()
    urlInput.value = url

    let error = document.getElementById("banner-error")

    if (url === "") {
        error.innerText = "ссылка на баннер пуста"
        urlInput.classList.add("error-input")
        urlInput.focus()
        return
    }

    SendRequest("/update-banner", {film_id: filmId, banner_url: url}).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return
        }

        banner.src = response.banner_url
        urlInput.value = ""
    })

    urlInput.classList.remove("error-input")
    error.innerText = ""
}

function GetBlock(block, className) {
    while (!block.classList.contains(className))
        block = block.parentNode

    return block
}

function ChangeBlock(initialBlock, className) {
    let block = GetBlock(initialBlock, className)
    let icon = block.getElementsByClassName("form-row-icon-interactive")[0]
    let error = document.getElementById("error")

    block.classList.remove("error-input")
    icon.classList.remove("error-icon")
    error.innerText = ""

    ShowSaveButton()
}

function RemoveFact(factIcon) {
    ChangeBlock(factIcon, "fact-block")

    let factsBlock = document.getElementById("facts")
    let block = GetBlock(factIcon, "fact-block")
    let index = 0

    while (factsBlock.children[index] != block)
        index++

    block.remove()
    factMarkups.splice(index, 1)
}

function AddFact() {
    let factsBlock = document.getElementById("facts")

    let factBlock = MakeElement("form-row fact-block", factsBlock)
    let block = MakeElement("table-block table-block-no-spacing fact", factBlock)
    let inputCell = MakeElement("table-cell", block)
    let factArea = MakeElement("fact-area", inputCell)
    let factInputHighlight = MakeElement("fact-input-highlight", factArea)
    let factInput = MakeElement("basic-textarea default-textarea fact-input", factArea, {tag: "textarea"})
    factInput.addEventListener("input", () => ChangeBlock(factBlock, "fact-block"))

    let spoilerBlock = MakeElement("fact-spoiler", inputCell)
    let label = MakeElement("", spoilerBlock, {tag: "label"})
    let spoiler = MakeElement("", label, {tag: "input", type: "checkbox"})
    let span = MakeElement("", label, {tag: "span", innerText: "Спойлер"})
    spoiler.addEventListener("change", () => ChangeBlock(factBlock, "fact-block"))

    let iconCell = MakeElement("table-cell table-cell-no-width form-row-top-icon", block)
    let icon = MakeElement("form-row-icon-interactive", iconCell, {title: "Удалить", innerHTML: REMOVE_ICON})
    icon.addEventListener("click", () => RemoveFact(icon))

    ChangeBlock(factBlock, "fact-block")
    factMarkups.push(new Markup(factInput, factInputHighlight, [], () => ChangeBlock(factBlock, "fact-block")))
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
        let spans = factMarkups[i].GetSpans()
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

function RemoveCite(citeIcon) {
    ChangeBlock(citeIcon, "cite-block")

    let citesBlock = document.getElementById("cites")
    let block = GetBlock(citeIcon, "cite-block")
    let index = 0

    while (citesBlock.children[index] != block)
        index++

    block.remove()
    citeMarkups.splice(index, 1)
}

function AddCite() {
    let citesBlock = document.getElementById("cites")

    let citeBlock = MakeElement("form-row cite-block", citesBlock)
    let block = MakeElement("table-block table-block-no-spacing cite", citeBlock)
    let inputCell = MakeElement("table-cell", block)
    let citeArea = MakeElement("cite-area", inputCell)
    let citeInputHighlight = MakeElement("cite-input-highlight", citeArea)
    let citeInput = MakeElement("basic-textarea default-textarea cite-input", citeArea, {tag: "textarea"})
    citeInput.addEventListener("input", () => ChangeBlock(citeBlock, "cite-block"))

    let iconCell = MakeElement("table-cell table-cell-no-width form-row-top-icon", block)
    let icon = MakeElement("form-row-icon-interactive", iconCell, {title: "Удалить", innerHTML: REMOVE_ICON})
    icon.addEventListener("click", () => RemoveCite(icon))

    ChangeBlock(citeBlock, "cite-block")
    citeMarkups.push(new Markup(citeInput, citeInputHighlight, [], () => ChangeBlock(citeBlock, "cite-block")))
}

function GetCites() {
    let citesBlock = document.getElementById("cites")
    let error = document.getElementById("error")
    let cites = []
    error.innerText = ""

    for (let i = 0; i < citesBlock.children.length; i++) {
        let citeBlock = citesBlock.children[i]
        let citeInput = citeBlock.getElementsByTagName("textarea")[0]
        let citeIcon = citeBlock.getElementsByClassName("form-row-icon-interactive")[0]
        let value = citeInput.value
        let spans = citeMarkups[i].GetSpans()
        citeInput.value = value

        if (value.trim() === "") {
            error.innerText = "Цитата пустая"
            citeIcon.classList.add("error-icon")
            citeBlock.classList.add("error-input")
            citeBlock.scrollIntoView({behaviour: "smooth"})
            return null
        }

        citeBlock.classList.remove("error-input")
        citeIcon.classList.remove("error-icon")
        cites.push({value: value, spans: spans})
    }

    return cites
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

    let cites = GetCites()
    if (cites === null)
        return

    let film = document.getElementById("film")
    let film_id = film.getAttribute("data-film-id")

    let button = document.getElementById("save-btn")
    let edited = document.getElementById("edited")
    let error = document.getElementById("error")
    error.innerText = ""

    SendRequest("/update-film", {film_id, name, movie_type, year, slogan, description, short_description, countries, genres, length, tops, facts, cites}).then(response => {
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
