const GALLERY_CLOSE_ICON = `<svg class="gallery-stroke-icon" width="30px" height="30px" viewBox="-0.5 0 25 25" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 21.32L21 3.32001" stroke-width="1.5"/>
    <path d="M3 3.32001L21 21.32" stroke-width="1.5"/>
</svg>`

const GALLERY_DOWNLOAD_ICON = `<svg class="gallery-stroke-icon" width="30px" height="30px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 15V18C20 19.1046 19.1046 20 18 20H6C4.89543 20 4 19.1046 4 18L4 15M8 11L12 15M12 15L16 11M12 15V3" stroke-width="1.5" fill="none" />
</svg>`

const GALLERY_LEFT_ICON = `<svg width="30px" height="30px" viewBox="100 -100 1024 1024" xmlns="http://www.w3.org/2000/svg">
    <path d="M768 903.232l-50.432 56.768L256 512l461.568-448 50.432 56.768L364.928 512z" />
</svg>`

const GALLERY_RIGHT_ICON = `<svg width="30px" height="30px" viewBox="-100 -100 1024 1024" xmlns="http://www.w3.org/2000/svg">
    <path d="M256 120.768L306.432 64 768 512l-461.568 448L256 903.232 659.072 512z" />
</svg>`

const GALLERY_LOADER_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="62px" height="62px" viewBox="-20 -20 296 296" fill="#000">
    <path d="M248,91.3V67H80v8H9c0,0,10.7,40.6,67.3,40.6c30.3,0,34.4,12.7,34.4,19.1c0,8.4-5.1,21.9-36.7,32.8V191h38.7
    c6.8-5.2,15.3-8.2,24.5-8.2s17.7,3.1,24.5,8.2H201c0,0,0-15.1,0-22.9c-23.4-7.7-38.7-20.4-38.7-34.8
    C162.3,110.6,200.1,92.5,248,91.3z M80,87c-52,0-52-4-52-4h52C80,83,80,85.4,80,87z M88,79v-4h152v4H88z"/>
    <animateTransform xmlns="http://www.w3.org/2000/svg" attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="0.9s" repeatCount="indefinite"/>
</svg>`

const GALLERY_TRANSITION = "transform 150ms"
const GALLERY_DEFAULT_MODE = "default"
const GALLERY_SWIPE_MODE = "swipe"
const GALLERY_HORIZONTAL_SWIPE_MODE = "swipe-horizontal"
const GALLERY_VERTICAL_SWIPE_MODE = "swipe-vertical"
const GALLERY_SCALE_MODE = "scale"

function Gallery(popupId) {
    this.popup = document.getElementById(popupId)
    this.body = document.getElementsByTagName("body")[0]
    this.open = false
    this.mode = GALLERY_DEFAULT_MODE

    this.offsetX = 0
    this.offsetY = 0

    this.BuildControls()
    this.BuildPhotos()
    this.InitEvents()
}

Gallery.prototype.BuildControls = function() {
    let topControls = this.MakeElement("gallery-top-controls", this.popup)

    let topInfo = this.MakeElement("gallery-top-info", topControls)
    this.positionSpan = this.MakeElement("gallery-top-info-text", topInfo, {}, "span")

    this.downloadLink = this.MakeElement("", null, {download: ""}, "a")
    let downloadIcon = this.MakeElement("gallery-top-control", topControls, {innerHTML: GALLERY_DOWNLOAD_ICON})
    downloadIcon.addEventListener("click", () => this.Download())

    let close = this.MakeElement("gallery-top-control", topControls, {innerHTML: GALLERY_CLOSE_ICON})
    close.addEventListener("click", () => this.Close())

    this.prev = this.MakeElement("gallery-prev-control", this.popup, {innerHTML: GALLERY_LEFT_ICON})
    this.prev.addEventListener("click", () => this.Prev())

    this.next = this.MakeElement("gallery-next-control", this.popup, {innerHTML: GALLERY_RIGHT_ICON})
    this.next.addEventListener("click", () => this.Next())
}

Gallery.prototype.BuildPhotos = function() {
    this.gallery = this.MakeElement("gallery-photos", this.popup)
    this.photos = []

    for (let image of document.getElementsByClassName("gallery-source"))
        this.AddPhoto(image)

    this.photoIndex = 0
}

Gallery.prototype.AddPhoto = function(image) {
    let index = this.photos.length
    image.setAttribute("data-index", index)
    image.addEventListener("click", () => this.ShowPhoto(image))

    let alt = image.getAttribute("alt")
    let previewUrl = image.getAttribute("src")
    let originalUrl = image.hasAttribute("data-src") ? image.getAttribute("data-src") : previewUrl

    let photo = this.MakeElement("gallery-photo", this.gallery)
    let photoImage = this.MakeElement("gallery-photo-image", photo, {alt: alt}, "img")
    let loader = this.MakeElement("gallery-loader", photo, {innerHTML: GALLERY_LOADER_ICON})

    photoImage.addEventListener("load", () => loader.remove())
    photo.addEventListener("contextmenu", (e) => e.preventDefault())
    this.photos.push({original: originalUrl, image: photoImage, loader: loader, block: photo})
}

Gallery.prototype.InitEvents = function() {
    this.gallery.addEventListener("mousedown", (e) => this.TouchStart(e))
    this.gallery.addEventListener("mousemove", (e) => this.TouchMove(e))
    this.gallery.addEventListener("mouseup", (e) => this.TouchEnd(e))
    this.gallery.addEventListener("mouseleave", (e) => this.TouchEnd(e))

    this.gallery.addEventListener("touchstart", (e) => this.TouchStart(e))
    this.gallery.addEventListener("touchmove", (e) => this.TouchMove(e))
    this.gallery.addEventListener("touchend", (e) => this.TouchEnd(e))
    this.gallery.addEventListener("touchleave", (e) => this.TouchEnd(e))

    this.gallery.addEventListener("transitionend", () => this.TransitionEnd())
    document.addEventListener("keydown", (e) => this.KeyDown(e))
}

Gallery.prototype.SetAttributes = function(element, attributes) {
    if (attributes === null)
        return

    for (let [name, value] of Object.entries(attributes)) {
        if (name == "innerText")
            element.innerText = value
        else if (name == "innerHTML")
            element.innerHTML = value
        else
            element.setAttribute(name, value)
    }
}

Gallery.prototype.MakeElement = function(className, parent = null, attributes = null, tagName = "div") {
    let element = document.createElement(tagName)
    element.className = className

    this.SetAttributes(element, attributes)

    if (parent !== null)
        parent.appendChild(element)

    return element
}

Gallery.prototype.Show = function() {
    if (this.photos.length == 1) {
        this.prev.classList.add("gallery-hidden")
        this.next.classList.add("gallery-hidden")
    }
    else {
        this.prev.classList.remove("gallery-hidden")
        this.next.classList.remove("gallery-hidden")
    }

    for (let delta of [0, -1, 1]) {
        let index = this.GetIndex(delta)
        let photo = this.photos[index]

        if (!photo.image.getAttribute("src"))
            photo.image.setAttribute("src", photo.original)
    }

    this.gallery.style.transform = `translate(${(-this.photoIndex + this.offsetX) * 100}%, ${this.offsetY * 100}%)`
    this.photos[this.photoIndex].image.style.transform = null
    this.positionSpan.innerText = `${this.photoIndex + 1} / ${this.photos.length}`
}

Gallery.prototype.ShowPhoto = function(image) {
    this.photoIndex = +image.getAttribute("data-index")

    this.Open()
    this.Show()
}

Gallery.prototype.Open = function() {
    if (this.open)
        return

    this.popup.classList.add("gallery-open")
    this.body.classList.add("gallery-body")
    this.open = true
    this.Show()
}

Gallery.prototype.Close = function() {
    this.popup.classList.remove("gallery-open")
    this.body.classList.remove("gallery-body")
    this.open = false
}

Gallery.prototype.GetIndex = function(delta = 0) {
    return (this.photoIndex + delta + this.photos.length) % this.photos.length
}

Gallery.prototype.Next = function() {
    this.gallery.style.transition = GALLERY_TRANSITION
    this.photoIndex = this.GetIndex(1)
    this.Show()
}

Gallery.prototype.Prev = function() {
    this.gallery.style.transition = GALLERY_TRANSITION
    this.photoIndex = this.GetIndex(-1)
    this.Show()
}

Gallery.prototype.Download = function() {
    this.downloadLink.setAttribute("href", this.photos[this.photoIndex].original)
    this.downloadLink.click()
}

Gallery.prototype.KeyDown = function(e) {
    if (!this.open)
        return

    if (e.code == "Escape") {
        e.preventDefault()
        this.Close()
    }
    else if (e.code == "ArrowLeft") {
        e.preventDefault()
        this.Prev()
    }
    else if (e.code == "ArrowRight") {
        e.preventDefault()
        this.Next()
    }
    else if (e.code == "KeyS" && e.ctrlKey) {
        e.preventDefault()
        this.Download()
    }
}

Gallery.prototype.GetPosition = function(e) {
    if (!e.touches)
        return {x: e.clientX / this.popup.clientWidth, y: e.clientY / this.popup.clientHeight}

    if (e.touches.length != 2)
        return {x: e.touches[0].clientX / this.popup.clientWidth, y: e.touches[0].clientY / this.popup.clientHeight}

    return {
        p1: {x: e.touches[0].clientX, y: e.touches[0].clientY}, 
        p2: {x: e.touches[1].clientX, y: e.touches[1].clientY}
    }
}

Gallery.prototype.TouchStart = function(e) {
    if (this.offsetX != 0 && e.touches && e.touches.length == 2)
        return

    this.isPressed = true
    this.position = this.GetPosition(e)
    this.initialPosition = this.GetPosition(e)
    this.mode = e.touches && e.touches.length == 2 ? GALLERY_SCALE_MODE : GALLERY_SWIPE_MODE
    this.gallery.style.transition = null
}

Gallery.prototype.TouchMove = function(e) {
    e.preventDefault()

    if (this.mode == GALLERY_SWIPE_MODE || this.mode == GALLERY_HORIZONTAL_SWIPE_MODE || this.mode == GALLERY_VERTICAL_SWIPE_MODE) {
        this.SwipeMove(e)
    }
    else if (this.mode == GALLERY_SCALE_MODE) {
        this.ScaleMove(e)
    }
}

Gallery.prototype.TouchEnd = function(e) {
    if (!this.isPressed)
        return

    if (this.mode == GALLERY_SWIPE_MODE || this.mode == GALLERY_HORIZONTAL_SWIPE_MODE || this.mode == GALLERY_VERTICAL_SWIPE_MODE) {
        this.SwipeEnd()
    }
    else if (this.mode == GALLERY_SCALE_MODE) {
        this.ScaleEnd()
    }

    this.isPressed = false
}

Gallery.prototype.SwipeMove = function(e) {
    if (!this.isPressed)
        return

    let position = this.GetPosition(e)
    let dx = position.x - this.initialPosition.x
    let dy = position.y - this.initialPosition.y

    if (this.photos.length > 1 && (Math.abs(dx) > Math.abs(dy) && this.mode == GALLERY_SWIPE_MODE || this.mode == GALLERY_HORIZONTAL_SWIPE_MODE)) {
        this.offsetX += position.x - this.position.x
        this.offsetY = 0
        this.mode = GALLERY_HORIZONTAL_SWIPE_MODE
    }
    else {
        this.offsetX = 0
        this.offsetY += position.y - this.position.y
        this.mode = GALLERY_VERTICAL_SWIPE_MODE
    }

    this.position = position
    this.Show()
}

Gallery.prototype.SwipeEnd = function() {
    if (Math.abs(this.offsetY) > 0.2) {
        this.Close()
    }
    else if (this.offsetX < -0.2) {
        this.photoIndex = this.GetIndex(1)
    }
    else if (this.offsetX > 0.2) {
        this.photoIndex = this.GetIndex(-1)
    }

    this.offsetX = 0
    this.offsetY = 0
    this.gallery.style.transition = GALLERY_TRANSITION
    this.mode = GALLERY_DEFAULT_MODE
    this.Show()
}

Gallery.prototype.GetDistance = function(p1, p2) {
    let dx = p2.x - p1.x
    let dy = p2.y - p1.y
    return Math.sqrt(dx * dx + dy * dy)
}

Gallery.prototype.ScaleMove = function(e) {
    if (!this.isPressed)
        return

    let block = this.photos[this.photoIndex].block
    let image = this.photos[this.photoIndex].image

    let position = this.GetPosition(e)
    let prevSize = this.GetDistance(this.position.p1, this.position.p2)
    let currSize = this.GetDistance(position.p1, position.p2)
    let scale = currSize / prevSize

    let x = (this.position.p1.x + this.position.p2.x) / 2 - (image.offsetLeft + image.clientWidth / 2)
    let y = (this.position.p1.y + this.position.p2.y) / 2 - (image.offsetTop + image.clientHeight / 2)

    image.style.transform = `translate(${x}px, ${y}px) scale(${Math.max(1, scale)}) translate(${-x}px, ${-y}px)`

    for (let bbox of document.getElementsByClassName("gallery-bbox")) {
        x = (this.position.p1.x + this.position.p2.x) / 2 - (bbox.offsetLeft + bbox.clientWidth / 2)
        y = (this.position.p1.y + this.position.p2.y) / 2 - (bbox.offsetTop + bbox.clientHeight / 2)

        bbox.style.transform = `translate(${x}px, ${y}px) scale(${Math.max(1, scale)}) translate(${-x}px, ${-y}px)`
    }
}

Gallery.prototype.ScaleEnd = function() {
    this.mode = GALLERY_DEFAULT_MODE
}

Gallery.prototype.TransitionEnd = function() {
    this.gallery.style.transition = null
}
