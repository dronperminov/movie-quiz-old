function Player(playerId, audio, onNext = null) {
    this.audio = audio
    this.onNext = onNext

    let block = document.getElementById(playerId)
    this.controls = block.getElementsByClassName("player-controls")[0]
    this.playIcon = block.getElementsByClassName("player-play-icon")[0]
    this.pauseIcon = block.getElementsByClassName("player-pause-icon")[0]
    this.nextIcon = block.getElementsByClassName("player-next-icon")[0]

    this.progressBar = block.getElementsByClassName("player-progress-bar")[0]
    this.currentProgress = block.getElementsByClassName("player-current-progress")[0]
    this.time = block.getElementsByClassName("player-time")[0]

    this.InitEvents()
    this.UpdateProgressBar()

    setInterval(() => this.UpdateLoop(), 10)
}

Player.prototype.InitEvents = function() {
    this.pressed = false

    this.audio.addEventListener("pause", () => {
        this.playIcon.classList.remove("player-hidden")
        this.pauseIcon.classList.add("player-hidden")
    })

    this.audio.addEventListener("play", () => {
        this.playIcon.classList.add("player-hidden")
        this.pauseIcon.classList.remove("player-hidden")
    })

    this.playIcon.addEventListener("click", () => this.Play())
    this.pauseIcon.addEventListener("click", () => this.Pause())

    if (this.onNext !== null)
        this.nextIcon.addEventListener("click", () => this.onNext())

    this.progressBar.parentNode.addEventListener("touchstart", (e) => this.ProgressMouseDown(e.touches[0].clientX - this.progressBar.parentNode.offsetLeft))
    this.progressBar.parentNode.addEventListener("touchmove", (e) => this.ProgressMouseMove(e.touches[0].clientX - this.progressBar.parentNode.offsetLeft))
    this.progressBar.parentNode.addEventListener("touchend", (e) => this.ProgressMouseUp())

    this.progressBar.parentNode.addEventListener("mousedown", (e) => this.ProgressMouseDown(e.offsetX))
    this.progressBar.parentNode.addEventListener("mousemove", (e) => this.ProgressMouseMove(e.offsetX))
    this.progressBar.parentNode.addEventListener("mouseup", (e) => this.ProgressMouseUp())
    this.progressBar.parentNode.addEventListener("mouseleave", (e) => this.ProgressMouseUp())
}

Player.prototype.UpdateLoop = function() {
    if (!this.audio.paused)
        this.UpdateProgressBar()
}

Player.prototype.Init = function() {
    this.audio.currentTime = 0
    this.audio.pause()

    this.controls.classList.remove("player-hidden")
    this.playIcon.classList.remove("player-hidden")
    this.pauseIcon.classList.add("player-hidden")
    this.time.classList.remove("player-hidden")

    if (this.onNext !== null)
        this.nextIcon.classList.remove("player-hidden")

    this.UpdateProgressBar()
}

Player.prototype.Hide = function() {
    this.controls.classList.add("player-hidden")
    this.playIcon.classList.add("player-hidden")
    this.pauseIcon.classList.add("player-hidden")
    this.nextIcon.classList.add("player-hidden")
    this.time.classList.add("player-hidden")
}

Player.prototype.TimeToString = function(time) {
    let seconds = `${Math.floor(time) % 60}`.padStart(2, '0')
    let minutes = `${Math.floor(time / 60)}`.padStart(2, '0')
    return `${minutes}:${seconds}`
}

Player.prototype.UpdateProgressBar = function() {
    this.currentProgress.style.width = `${(this.audio.currentTime / this.audio.duration) * 100}%`
    this.time.innerText = `${this.TimeToString(this.audio.currentTime)} / ${this.TimeToString(this.audio.duration)}`

    if ('setPositionState' in navigator.mediaSession)
        navigator.mediaSession.setPositionState({duration: this.audio.duration, playbackRate: this.audio.playbackRate, position: this.audio.currentTime})
}

Player.prototype.Play = function() {
    this.audio.play()
}

Player.prototype.Pause = function() {
    this.audio.pause()
}

Player.prototype.Seek = function(time) {
    this.audio.currentTime = time
    this.UpdateProgressBar()
}

Player.prototype.ProgressMouseDown = function(x) {
    this.paused = this.audio.paused
    this.pressed = true

    let part = x / this.progressBar.clientWidth
    this.audio.currentTime = part * this.audio.duration
    this.audio.pause()

    this.UpdateProgressBar()
}

Player.prototype.ProgressMouseMove = function(x) {
    if (!this.pressed)
        return

    let part = x / this.progressBar.clientWidth
    this.audio.currentTime = part * this.audio.duration
    this.UpdateProgressBar()
}

Player.prototype.ProgressMouseUp = function() {
    if (!this.pressed)
        return

    this.pressed = false

    if (!this.paused)
        this.audio.play()
}
