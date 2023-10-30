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

    let description = GetTextField("description")
    if (description === null)
        return

    let short_description = GetTextField("short-description")
    if (short_description === null)
        return

    let countries = GetTextListField("countries", "Страна выхода не указана")
    if (countries === null)
        return

    let genres = GetTextListField("genres", "Жанр не указан")
    if (genres === null)
        return

    let length = GetNumberField("length")
    let tops = GetMultiSelect("top-lists", null)

    let film = document.getElementById("film")
    let film_id = film.getAttribute("data-film-id")

    let button = document.getElementById("save-btn")
    let error = document.getElementById("error")
    error.innerText = ""

    SendRequest("/update-film", {film_id, name, movie_type, year, slogan, description, short_description, countries, genres, length, tops}).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return
        }

        button.classList.add("hidden")
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
