const REMOVE_ICON = `<svg class="form-svg-fill-icon" width="20px" height="20px" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 4h3c.6 0 1 .4 1 1v1H3V5c0-.6.5-1 1-1h3c.2-1.1 1.3-2 2.5-2s2.3.9 2.5 2zM8 4h3c-.2-.6-.9-1-1.5-1S8.2 3.4 8 4zM4 7h11l-.9 10.1c0 .5-.5.9-1 .9H5.9c-.5 0-.9-.4-1-.9L4 7z"/>
</svg>`

const PLAY_ICON = `<svg class="form-svg-fill-icon" width="20px" height="20px" viewBox="-0.3 -0.05 7.1 7.1" xmlns="http://www.w3.org/2000/svg">
    <path d="M5.495,2.573 L1.501,0.142 C0.832,-0.265 0,0.25 0,1.069 L0,5.931 C0,6.751 0.832,7.264 1.501,6.858 L5.495,4.428 C6.168,4.018 6.168,2.983 5.495,2.573"></path>
</svg>`

const PLAYER_HTML = `<div class="player-controls player-hidden">
        <svg class="player-controls-icon player-hidden player-play-icon" width="20px" height="20px" viewBox="-0.3 -0.05 7.1 7.1" xmlns="http://www.w3.org/2000/svg">
            <path d="M5.495,2.573 L1.501,0.142 C0.832,-0.265 0,0.25 0,1.069 L0,5.931 C0,6.751 0.832,7.264 1.501,6.858 L5.495,4.428 C6.168,4.018 6.168,2.983 5.495,2.573" />
        </svg>

        <svg class="player-controls-icon player-hidden player-pause-icon" width="20px" height="20px" viewBox="-0.7 -0.05 8.1 8.1" xmlns="http://www.w3.org/2000/svg">
            <path d="M1,0 C0.448,0 0,0.448 0,1 L0,7 C0,7.552 0.448,8 1,8 C1.552,8 2,7.552 2,7 L2,1 C2,0.448 1.552,0 1,0 M6,1 L6,7 C6,7.552 5.552,8 5,8 C4.448,8 4,7.552 4,7 L4,1 C4,0.448 4.448,0 5,0 C5.552,0 6,0.448 6,1" />
        </svg>

    </div>
    <div class="player-controls">
        <svg class="player-controls-icon player-hidden player-next-icon" width="20px" height="20px" viewBox="0 0 12 12" xmlns="http://www.w3.org/2000/svg">
            <path d="M11.684,4.694 L7.207,7.825 C6.571,8.254 6,7.846 6,7.132 L6,5.141 L1.78,7.825 C1.145,8.254 0,7.846 0,7.132 L0,0.869 C0,0.155 1.145,-0.253 1.78,0.175 L6,2.86 L6,0.869 C6,0.155 6.571,-0.253 7.207,0.175 L11.516,3.307 C12.03,3.654 12.198,4.347 11.684,4.694" transform="scale(1 1.4)">
        </svg>
    </div>

    <div class="player-progress">
        <div class="player-progress-bar">
            <div class="player-current-progress"></div>
        </div>
    </div>

    <div class="player-time player-hidden"></div>`

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

function AddParsedAudio(track) {
    let dataAttributes = {
        "data-link": track.link,
        "data-artist": track.artist,
        "data-track": track.title,
        "data-album-id": track.album_id,
        "data-track-id": track.track_id,
        "data-downloaded": "false"
    }

    let block = document.getElementById("audios")
    let row = MakeElement("form-row audio-block", block, {id: `audio-block-${track.link}`, ...dataAttributes})
    let tableBlock = MakeElement("table-block table-block-no-spacing", row)
    let nameCell = MakeElement("table-cell", tableBlock, {innerText: `${track.artist} - ${track.title}`})
    let iconCell = MakeElement("table-cell table-cell-no-width", tableBlock)
    let icon = MakeElement("form-row-icon-interactive icons-controls", iconCell, {innerHTML: REMOVE_ICON})
    icon.addEventListener("click", () => RemoveAudio(icon))

    let playerBlock = MakeElement("table-block table-block-no-spacing", row, {id: `play-audio-${track.link}`})
    let playCell = MakeElement("table-cell table-cell-no-width table-cell-middle center", playerBlock)
    let playIcon = MakeElement("form-row-icon-interactive", playCell, {innerHTML: PLAY_ICON})
    playIcon.addEventListener("click", () => PlayAudio(track.link))

    let playerCell = MakeElement("table-cell table-cell-middle", playerBlock)
    let playerDiv = MakeElement("", playerCell, {id: `player-${track.link}`})
    let audio = MakeElement("", playerDiv, {tag: "audio", id: `audio-${track.link}`, preload: "metadata", "data-link": track.link})
    let player = MakeElement("player", playerDiv, {innerHTML: PLAYER_HTML})

    let error = MakeElement("error", row, {id: `error-${track.link}`})

    AddPlayer(players, audio)
}

function ParseAudios() {
    let code = GetTextField("audios-code", "Поле ввода пустое")
    if (code === null)
        return

    let error = document.getElementById("error")
    let parseBtn = document.getElementById("parse-btn")
    let saveBtn = document.getElementById("save-btn")

    parseBtn.setAttribute("disabled", "")
    saveBtn.setAttribute("disabled", "")
    saveBtn.classList.remove("hidden")

    return SendRequest("/parse-audios", {code: code}).then(response => {
        parseBtn.removeAttribute("disabled")
        saveBtn.removeAttribute("disabled")

        if (response.status != "success") {
            error.innerText = "Некоторые треки не удалось скачать"
            return
        }

        for (let track of response.tracks)
            AddParsedAudio(track)

        let countSpan = document.getElementById("audios-count")
        countSpan.innerText = document.getElementById("audios").children.length
    })
}

function RemoveAudio(icon) {
    ChangeBlock(icon, "audio-block")
    let block = GetBlock(icon, "audio-block")
    block.remove()

    let countSpan = document.getElementById("audios-count")
    countSpan.innerText = document.getElementById("audios").children.length
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

    let countSpan = document.getElementById("facts-count")
    countSpan.innerText = factsBlock.children.length
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

    let countSpan = document.getElementById("facts-count")
    countSpan.innerText = factsBlock.children.length
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
    let countSpan = document.getElementById("cites-count")
    countSpan.innerText = citesBlock.children.length
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

    let countSpan = document.getElementById("cites-count")
    countSpan.innerText = citesBlock.children.length
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

function GetAudios() {
    let audios = []

    for (let audioBlock of document.getElementById("audios").children) {
        audios.push({
            link: audioBlock.getAttribute("data-link"),
            artist: audioBlock.getAttribute("data-artist"),
            track: audioBlock.getAttribute("data-track"),
            album_id: +audioBlock.getAttribute("data-album-id"),
            track_id: +audioBlock.getAttribute("data-track-id"),
            downloaded: audioBlock.getAttribute("data-downloaded") == "true"
        })
        console.log(audioBlock)
        console.log(audios[audios.length - 1])
    }

    return audios
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

    let audios = GetAudios()

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

    SendRequest("/update-film", {film_id, name, movie_type, year, slogan, description, short_description, countries, genres, length, tops, audios, facts, cites}).then(response => {
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
