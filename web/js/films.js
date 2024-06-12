function GetYears() {
    let error = document.getElementById("error")

    let startYearInput = document.getElementById("years-start")
    let endYearInput = document.getElementById("years-end")

    let startYear = startYearInput.value
    let endYear = endYearInput.value
    let year = new Date().getFullYear()

    if (startYear.match(/^\d+$/g))
        startYear = Math.max(Math.min(+startYear, year), +startYearInput.getAttribute("min")).toString()

    if (endYear.match(/^\d+$/g))
        endYear = Math.max(Math.min(+endYear, year), +endYearInput.getAttribute("min")).toString()

    startYearInput.value = startYear
    endYearInput.value = endYear

    if (startYear.match(/^(\d\d\d\d)?$/g) === null) {
        error.innerText = "Начало периода введено некорректно"
        startYearInput.focus()
        startYearInput.classList.add("error-input")
        return null
    }

    if (endYear.match(/^(\d\d\d\d)?$/g) === null) {
        error.innerText = "Конец периода введён некорректно"
        endYearInput.focus()
        endYearInput.classList.add("error-input")
        return null
    }

    startYearInput.classList.remove("error-input")
    endYearInput.classList.remove("error-input")

    if (startYear.match(/^\d\d\d\d$/g) !== null && endYear.match(/^\d\d\d\d$/g) !== null)
        return {start: Math.min(+startYear, +endYear), end: Math.max(+startYear, +endYear)}

    return {start: startYear, end: endYear}
}

function ProcessKM(value) {
    if (value.match(/^\d+$/g))
        return +value

    if (value.match(/^\d+(\.\d{1,3})?[kKкК]$/g))
        return Math.round((+value.substr(0, value.length - 1)) * 1000)

    if (value.match(/^\d+(\.\d{1,6})?[mMмМ]$/g))
        return Math.round((+value.substr(0, value.length - 1)) * 1000000)

    return null
}

function GetVotes() {
    let error = document.getElementById("error")

    let startVotesInput = document.getElementById("votes-start")
    let endVotesInput = document.getElementById("votes-end")

    let startVotes = startVotesInput.value
    let endVotes = endVotesInput.value

    if (ProcessKM(startVotes) !== null)
        startVotes = Math.max(ProcessKM(startVotes), +startVotesInput.getAttribute("min")).toString()

    if (ProcessKM(endVotes) !== null)
        endVotes = Math.max(ProcessKM(endVotes), +endVotesInput.getAttribute("min")).toString()

    startVotesInput.value = startVotes
    endVotesInput.value = endVotes

    if (startVotes.match(/^(\d+)?$/g) === null) {
        error.innerText = "Минимальное количество оценок введено некорректно"
        startVotesInput.focus()
        startVotesInput.classList.add("error-input")
        return null
    }

    if (endVotes.match(/^(\d+)?$/g) === null) {
        error.innerText = "Максимальное количество оценко введено некорректно"
        endVotesInput.focus()
        endVotesInput.classList.add("error-input")
        return null
    }

    startVotesInput.classList.remove("error-input")
    endVotesInput.classList.remove("error-input")

    if (startVotes.match(/^\d+$/g) !== null && endVotes.match(/^\d+$/g) !== null)
        return {start: Math.min(+startVotes, +endVotes), end: Math.max(+startVotes, +endVotes)}

    return {start: startVotes, end: endVotes}
}

function ChangeYear(inputId) {
    let input = document.getElementById(inputId)
    let error = document.getElementById("error")

    input.classList.remove("error-input")
    error.innerText = ""
}

function SearchFilms() {
    let queryInput = document.getElementById("query")
    let query = queryInput.value.trim()
    queryInput.value = query

    let params = [`query=${encodeURIComponent(query)}`]

    let years = GetYears()
    if (years === null)
        return

    if (years.start != "")
        params.push(`start_year=${years.start}`)

    if (years.end != "")
        params.push(`end_year=${years.end}`)

    let votes = GetVotes()
    if (votes === null)
        return

    if (votes.start != "")
        params.push(`start_votes=${votes.start}`)

    if (votes.end != "")
        params.push(`end_votes=${votes.end}`)

    for (let movieType of GetMultiSelectNames("movie-types"))
        if (document.getElementById(`movie-types-${movieType}`).checked)
            params.push(`movie_types=${movieType}`)

    for (let topList of GetMultiSelectNames("top-lists"))
        if (document.getElementById(`top-lists-${topList}`).checked)
            params.push(`top_lists=${topList}`)

    for (let production of GetMultiSelectNames("production"))
        if (document.getElementById(`production-${production}`).checked)
            params.push(`production=${production}`)

    window.location = `/films?${params.join("&")}`   
}
