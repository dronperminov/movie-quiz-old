function LoadAudio(audio, errorId = "error") {
    let error = document.getElementById(errorId)
    error.innerText = ""

    if (audio.hasAttribute("data-src")) {
        return new Promise((resolve, reject) => {
            audio.src = audio.getAttribute("data-src")
            resolve(true)
        })
    }

    return SendRequest("/get-direct-link", {track_id: audio.getAttribute("data-track-id")}).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return false
        }

        audio.src = response.direct_link
        return true
    })
}

function AddPlayer(players, audio) {
    let trackId = audio.getAttribute("data-track-id")

    audio.addEventListener("loadedmetadata", () => {
        let player = new Player(`player-${trackId}`, audio)
        player.Init()
        player.Play()
        players[trackId] = player
    })

    audio.addEventListener("play", () => PausePlayers(trackId))
}

function InitPlayers() {
    let players = {}

    for (let audio of document.getElementsByTagName("audio"))
        AddPlayer(players, audio)

    return players
}

function PausePlayers(targetTrackId) {
    for (let trackId of Object.keys(players))
        if (trackId != targetTrackId)
            players[trackId].Pause()
}

function PlayAudio(trackId) {
    let audio = document.getElementById(`audio-${trackId}`)
    let block = document.getElementById(`play-audio-${trackId}`)

    LoadAudio(audio, `error-${trackId}`).then(success => {
        if (!success)
            return

        PausePlayers(trackId)

        block.classList.remove("table-block")
        block.children[1].classList.remove("table-cell")
        block.children[0].remove()
    })
}
