function ShowAnswer() {
    let button = document.getElementById("show-btn")
    let answer = document.getElementById("answer")
    answer.classList.remove("hidden")
    button.remove()

    for (let span of document.getElementsByClassName("spoiler"))
        span.classList.remove("spoiler-hidden")
}

function CheckAnswer(isCorrect) {
    let question = document.getElementById("question")
    let questionType = question.getAttribute("data-question-type")
    let filmId = +question.getAttribute("data-film-id")

    let error = document.getElementById("check-answer-error")
    error.innerText = ""

    SendRequest("/add-statistic", {question_type: questionType, film_id: filmId, correct: isCorrect}).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return
        }

        let block = document.getElementById("check-answer")
        block.remove()
        window.location = "/question"
    })
}

function OpenActor(block) {
    block.classList.remove("actor-preview-blur")
}
