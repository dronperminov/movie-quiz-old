function LoadProfileImage() {
    let input = document.getElementById("profile-input")
    input.click()
}

function UpdateProfileImage(e) {
    let error = document.getElementById("error")
    let input = document.getElementById("profile-input")
    let image = document.getElementById("profile-image")
    image.src = URL.createObjectURL(input.files[0])

    let formData = new FormData()
    formData.append("image", input.files[0])

    error.innerText = ""

    SendRequest("/update-avatar", formData).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return
        }
    })
}

function ChangeTheme() {
    let theme = document.getElementById("theme").value
    let html = document.getElementsByTagName("html")[0]
    html.setAttribute("data-theme", theme)

    let themeColors = {
        "dark": "#1e2027",
        "light": "#f7e06e"
    }

    let themeColor = document.querySelector('meta[name="theme-color"]')
    themeColor.setAttribute("content", themeColors[theme])

    ShowSaveButton()
}

function SaveSettings() {
    let fullname = GetTextField("fullname", "Полное имя не заполнено")
    if (fullname === null)
        return

    let showQuestionsCount = GetMultiSelect("show-questions-count", null)
    if (showQuestionsCount === null)
        return

    let questionYears = GetMultiSelect("question-years", null, "Не выбран ни один год выхода")
    if (questionYears === null)
        return

    let questions = GetMultiSelect("questions", null, "Не выбран ни один тип вопросов")
    if (questions === null)
        return

    let movieProductions = GetMultiSelect("movie-productions", null, "Не выбрано ни одного производства")
    if (movieProductions === null)
        return

    let movieTypes = GetMultiSelect("movie-types", null, "Не выбрано ни одного типа КМС")
    if (movieTypes === null)
        return

    let topLists = GetMultiSelect("top-lists", null)
    if (topLists === null)
        return

    let hideActors = GetMultiSelect("hide-actors", null)
    if (hideActors === null)
        return

    let data = {
        fullname: fullname,
        theme: document.getElementById("theme").value,
        question_years: questionYears.map((value) => value.split("-").map(v => +v)),
        questions: questions,
        movie_productions: movieProductions,
        movie_types: movieTypes,
        top_lists: topLists,
        hide_actors: hideActors.length > 0,
        show_questions_count: showQuestionsCount.length > 0,
        facts_mode: document.getElementById("facts-mode").value
    }

    let button = document.getElementById("save-btn")
    let error = document.getElementById("error")
    let info = document.getElementById("info")
    error.innerText = ""
    info.innerText = ""

    SendRequest("/update-settings", data).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return
        }

        button.classList.add("hidden")
        info.innerText = `Настройкам соответствует ${response.films_count} ${GetWordForm(response.films_count, ["фильмов", "фильма", "фильм"])}`
    })
}

function UpdateActionsVisibility() {
    let block = document.getElementById("actions")

    if (block.children.length < 3)
        block.classList.add("hidden")
    else
        block.classList.remove("hidden")
}

function ResetStatistic() {
    if (!confirm("Вы уверены, что хотите сбросить всю статистику? Отменить данное действие будет невозможно!"))
        return

    let button = document.getElementById("reset-statistic-btn")
    let error = document.getElementById("actions-error")
    error.innerText = ""

    SendRequest("/clear-statistic", {}).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return
        }

        button.remove()
        UpdateActionsVisibility()
    })
}
