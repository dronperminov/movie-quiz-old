function LoadAudio(audio, errorId = "error") {
    let error = document.getElementById(errorId)
    error.innerText = ""

    if (audio.hasAttribute("data-src")) {
        return new Promise((resolve, reject) => {
            audio.src = audio.getAttribute("data-src")
            resolve(true)
        })
    }

    return SendRequest("/get-direct-link", {track_id: audio.getAttribute("data-link")}).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return false
        }

        audio.src = response.direct_link
        return true
    })
}

function AddPlayer(players, audio) {
    let link = audio.getAttribute("data-link")

    audio.addEventListener("loadedmetadata", () => {
        let player = new Player(`player-${link}`, audio)
        player.Init()
        player.Play()
        players[link] = player
    })

    audio.addEventListener("play", () => PausePlayers(link))
}

function InitPlayers() {
    let players = {}

    for (let audio of document.getElementsByTagName("audio"))
        AddPlayer(players, audio)

    return players
}

function PausePlayers(targetLink) {
    for (let link of Object.keys(players))
        if (link != targetLink)
            players[link].Pause()
}

function PlayAudio(link) {
    let audio = document.getElementById(`audio-${link}`)
    let block = document.getElementById(`play-audio-${link}`)

    LoadAudio(audio, `error-${link}`).then(success => {
        if (!success)
            return

        PausePlayers(link)

        block.classList.remove("table-block")
        block.children[1].classList.remove("table-cell")
        block.children[0].remove()
    })
}
