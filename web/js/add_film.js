const REMOVE_ICON = `<svg class="form-svg-fill-icon" width="20px" height="20px" viewBox="2 2 16 16" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 4h3c.6 0 1 .4 1 1v1H3V5c0-.6.5-1 1-1h3c.2-1.1 1.3-2 2.5-2s2.3.9 2.5 2zM8 4h3c-.2-.6-.9-1-1.5-1S8.2 3.4 8 4zM4 7h11l-.9 10.1c0 .5-.5.9-1 .9H5.9c-.5 0-.9-.4-1-.9L4 7z"/>
</svg>`

const PLAY_ICON = `<svg class="form-svg-fill-icon" width="20px" height="20px" viewBox="-1 0 8 8" xmlns="http://www.w3.org/2000/svg">
    <path d="M5.495,2.573 L1.501,0.142 C0.832,-0.265 0,0.25 0,1.069 L0,5.931 C0,6.751 0.832,7.264 1.501,6.858 L5.495,4.428 C6.168,4.018 6.168,2.983 5.495,2.573"></path>
</svg>`

const IMAGES_ICON = `<svg class="film-stroke-icon" width="15px" height="15px" viewBox="2 2 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M7 5V19M17 5V19M3 8H7M17 8H21M3 16H7M17 16H21M3 12H7M17 12H21M6.2 20H17.8C18.9201 20 19.4802 20 19.908 19.782C20.2843 19.5903 20.5903 19.2843 20.782 18.908C21 18.4802 21 17.9201 21 16.8V7.2C21 6.0799 21 5.51984 20.782 5.09202C20.5903 4.71569 20.2843 4.40973 19.908 4.21799C19.4802 4 18.9201 4 17.8 4H6.2C5.0799 4 4.51984 4 4.09202 4.21799C3.71569 4.40973 3.40973 4.71569 3.21799 5.09202C3 5.51984 3 6.07989 3 7.2V16.8C3 17.9201 3 18.4802 3.21799 18.908C3.40973 19.2843 3.71569 19.5903 4.09202 19.782C4.51984 20 5.07989 20 6.2 20Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`

const CITES_ICON = `<svg class="film-fill-icon" height="15px" width="15px" xmlns="http://www.w3.org/2000/svg" viewBox="-15 -15 221.029 221.029">
    <path d="M44.33,88.474v15.377h38.417v82.745H0v-82.745h0.002V88.474c0-31.225,8.984-54.411,26.704-68.918
    C38.964,9.521,54.48,4.433,72.824,4.433v44.326C62.866,48.759,44.33,48.759,44.33,88.474z M181.107,48.759V4.433
    c-18.343,0-33.859,5.088-46.117,15.123c-17.72,14.507-26.705,37.694-26.705,68.918v15.377h0v82.745h82.744v-82.745h-38.417V88.474
    C152.613,48.759,171.149,48.759,181.107,48.759z"/>
</svg>`

const FACTS_ICON = `<svg class="film-fill-icon" height="15px" width="15px" viewBox="40 40 432 432"xmlns="http://www.w3.org/2000/svg">
    <path d="M192.021,128.021 L448.043,128.021 L448.043,85.354 L192.021,85.354 L192.021,128.021 Z M64.043,170.688 L149.376,170.688 L149.376,85.333 L64.043,85.333 L64.043,170.688 Z M192.021,213.354 L448.043,213.354 L448.043,170.688 L192.021,170.688 L192.021,213.354 Z M362.688,384.021 L448.043,384.021 L448.043,298.666 L362.688,298.666 L362.688,384.021 Z M64,341.354 L320,341.354 L320,298.666 L64,298.666 L64,341.354 Z M64.043,426.688 L320.043,426.688 L320.043,384.021 L64.043,384.021 L64.043,426.688 Z" />
</svg>`

function GetFilmIds(links) {
    let filmIds = []
    let filmIdsSet = new Set()

    for (let link of links) {
        let match = /\/(film|series)\/(?<film>\d+)\/?(\?.*)?$/g.exec(link).groups
        let filmId = +match.film

        if (filmIdsSet.has(filmId))
            continue

        filmIds.push(filmId)
        filmIdsSet.add(filmId)
    }

    return filmIds
}

function RemoveFilm(filmId, block) {
    if (!confirm("Вы уверены, что хотите удалить этот фильм?"))
        return

    delete filmsCollection[filmId]
    block.remove()

    let filmsBlock = document.getElementById("films")
    let addBtn = document.getElementById("add-btn")

    if (filmsBlock.children.length == 0)
        addBtn.classList.add("hidden")
}

function DownloadImages(images, film, error) {
    let count = document.getElementById(`film-${film.film_id}-images-icon`)
    count.innerText = `0 / ${images.length}`
    error.innerText = ""

    let added = 0
    let fetches = []

    for (let image of images) {
        fetches.push(SendRequest("/download-image", {"film_id": film.film_id, "image": image}).then(response => {
            if (response.status != "success" || response.result == "error") {
                error.innerText = "не удалось скачать некоторые кадры"
                return false
            }

            added++
            filmsCollection[film.film_id].images.push({"url": response.url})
            count.innerText = `${added} / ${images.length}`
            return true
        }))
    }

    return fetches
}

function FinalizeDownload(results, filmBlock, addIcon) {
    for (let result of results)
        if (!result)
            return

    filmBlock.classList.add("done")
    addIcon.classList.add("hidden")

    let addBtn = document.getElementById("add-btn")
    addBtn.setAttribute("disabled", "")

    let filmsBlock = document.getElementById("films")
    for (let filmBlock of filmsBlock.children)
        if (!filmBlock.classList.contains("done"))
            return

    addBtn.removeAttribute("disabled")
}

function AddFilmImages(film, filmBlock, addIcon, error) {
    error.innerText = ""
    addIcon.classList.add("hidden")

    let images = film.images
    film.images = []

    Promise.all(DownloadImages(images, film, error)).then(results => FinalizeDownload(results, filmBlock, addIcon))
}

function AddParsedFilm(film) {
    let countries = film.countries.length > 0 ? film.countries[0] + (film.countries.length > 1 ? "..." : "") : ""
    let directors = film.directors.length > 0 ? `, реж. ${film.directors[0].name}` + (film.directors.length > 1 ? "..." : "") : ""

    let filmsBlock = document.getElementById("films")

    let tableBlock = MakeElement("film-block table-block table-block-no-spacing", filmsBlock)
    let error = MakeElement("error", tableBlock)

    let filmCell = MakeElement("table-cell", tableBlock)
    let iconsCell = MakeElement("table-cell table-cell-no-width form-row-top-icon center", tableBlock)
    let removeIcon = MakeElement("form-row-icon-interactive film-icon", iconsCell, {id: `film-${film.film_id}-remove-icon`, innerHTML: REMOVE_ICON, title: "Удалить фильм"})
    removeIcon.addEventListener("click", () => RemoveFilm(film.film_id, tableBlock))
    let addIcon = MakeElement("form-row-icon-interactive film-icon", iconsCell, {id: `film-${film.film_id}-add-icon`, innerHTML: PLAY_ICON, title: "Запустить добавление"})
    addIcon.addEventListener("click", () => AddFilmImages(film, tableBlock, addIcon, error))

    let filmBlock = MakeElement("", filmCell, {id: `film-${film.film_id}`})

    let posterBlock = MakeElement("film-poster", filmBlock)
    let poster = MakeElement("", posterBlock, {tag: "img", alt: `Постер к фильму ${film.name}`, src: film.poster.previewUrl, loading: "lazy"})

    let filmInfo = MakeElement("film-info", filmBlock)
    let filmName = MakeElement("text", filmInfo, {innerHTML: `<a id="film-${film.film_id}-link" target="_blank">${film.name}</a> ${film.year}`})
    let filmCountryDirectors = MakeElement("text film-country-directors", filmInfo, {innerText: `${countries}${directors}`})
    let filmGenres = MakeElement("text film-genres", filmInfo, {innerText: film.genres.join(", ")})
    let filmIcons = MakeElement("film-icons", filmInfo)

    MakeElement("film-icon", filmIcons, {innerHTML: `${IMAGES_ICON}<span class="film-icon-value"><span id="film-${film.film_id}-images-icon">0 / ${film.images.length}</span></span>`, title: "Кадры"})

    if (film.cites.length > 0)
        MakeElement("film-icon", filmIcons, {innerHTML: `${CITES_ICON}<span class="film-icon-value">${film.cites.length}</span>`, title: "Цитаты"})

    if (film.facts.length > 0)
        MakeElement("film-icon", filmIcons, {innerHTML: `${FACTS_ICON}<span class="film-icon-value">${film.facts.length}</span>`, title: "Факты"})

    if (document.getElementById("download-images-immediately").checked)
        addIcon.click()

    return film
}

function ParseFilms() {
    let links = GetLinesField("links", /\/(film|series)\/(?<film>\d+)\/?(\?.*)?$/g, "Не введено ни одной ссылки", "Среди введённых ссылок нет ведущих на фильм")
    if (links === null)
        return

    let filmsBlock = document.getElementById("films")
    filmsBlock.innerHTML = ""

    let addBtn = document.getElementById("add-btn")
    addBtn.classList.add("hidden")
    addBtn.setAttribute("disabled", "")

    let parseBtn = document.getElementById("parse-btn")
    parseBtn.setAttribute("disabled", "")

    let error = document.getElementById("error")
    error.innerText = ""

    let info = document.getElementById("add-info")
    info.innerText = ""

    let filmIds = GetFilmIds(links)

    SendRequest("/parse-films", {film_ids: filmIds}).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
        }
        else if (response.films.length == 0) {
            info.innerText = "все фильмы уже были добавлены ранее"
        }
        else {
            addBtn.classList.remove("hidden")

            for (let film of response.films)
                filmsCollection[film.film_id] = AddParsedFilm(film)
        }

        parseBtn.removeAttribute("disabled")
    })
}

function AddFilms() {
    let error = document.getElementById("add-error")
    error.innerText = ""

    let info = document.getElementById("add-info")
    info.innerText = ""

    SendRequest("/add-films", {films: Object.values(filmsCollection)}).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return
        }

        info.innerText = "Фильмы успешно добавлены"

        let addBtn = document.getElementById("add-btn")
        addBtn.classList.add("hidden")

        for (let filmId of Object.keys(filmsCollection)) {
            let icon = document.getElementById(`film-${filmId}-remove-icon`)
            icon.classList.add("hidden")

            let link = document.getElementById(`film-${filmId}-link`)
            link.setAttribute("href", `/films/${filmId}`)
        }

        filmsCollection = {}
    })
}
