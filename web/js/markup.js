function Markup(editableBox, highlightBox, spans) {
    this.editableBox = editableBox
    this.highlightBox = highlightBox
    this.spans = spans
    this.tabSpaces = ' '

    this.editableBox.addEventListener('input', (e) => this.Input(e))
    this.editableBox.addEventListener('cnahge', () => this.Highlight())
    this.editableBox.addEventListener('keydown', (e) => this.KeyDown(e))

    this.Highlight()
}

Markup.prototype.HaveIntersection = function(span, start, end) {
    if (span.start <= start && start <= span.end)
        return true

    if (span.start <= end && end <= span.end)
        return true

    if (start <= span.start && span.end <= end)
        return true

    return false
}

Markup.prototype.HaveInsideSpan = function(start, end) {
    for (let span of this.spans)
        if (this.HaveIntersection(span, start, end))
            return true

    return false
}

Markup.prototype.TryAddSpan = function(e) {
    let start = this.editableBox.selectionStart
    let end = this.editableBox.selectionEnd

    if (start == end)
        return

    if (!this.HaveInsideSpan(start, end))
        this.spans.push({start: start, end: end})

    this.editableBox.selectionStart = this.editableBox.selectionEnd
    e.preventDefault()
}

Markup.prototype.TryRemoveSpan = function(e) {
    let start = this.editableBox.selectionStart
    let end = this.editableBox.selectionEnd
    let spans = this.spans.filter(span => !this.HaveIntersection(span, start, end))

    if (spans.length == this.spans.length)
        return

    this.spans = spans
    this.editableBox.selectionStart = this.editableBox.selectionEnd
    e.preventDefault()
}

// TODO
Markup.prototype.ShiftSpans = function(e) {
    this.spans = []
}

Markup.prototype.Input = function(e) {
    this.ShiftSpans(e)
    this.Highlight()
}

Markup.prototype.KeyDown = function(e) {
    if (e.key == "Enter") {
        this.TryAddSpan(e)
    }
    else if (e.key == "Escape") {
        this.TryRemoveSpan(e)
    }

    this.Highlight()
}

Markup.prototype.SpanLine = function(text, offset) {
    let endOffset = offset + text.length
    let spans = []

    for (let span of this.spans.sort((a, b) => b.start - a.start)) {
        if (span.start < offset || span.end > endOffset)
            continue

        spans.push(span)
        let before = text.substr(0, span.start - offset)
        let inside = text.substr(span.start - offset, span.end - span.start)
        let after = text.substr(span.end - offset)
        text = `${before}<span class="spoiler">${inside}</span>${after}`
    }

    return {text, spans}
}

Markup.prototype.IsWhiteSpace = function(line) {
    return line.match(/^\s*$/gi) != null
}

Markup.prototype.FixHeight = function() {
    if (this.editableBox.clientHeight == this.editableBox.scrollHeight)
        return

    this.editableBox.style.height = "5px"
    this.editableBox.style.height = `${this.editableBox.scrollHeight}px`
}

Markup.prototype.Highlight = function() {
    this.highlightBox.innerHTML = ""

    let text = this.editableBox.value
    let offset = 0
    let spans = []

    for (let line of text.split("\n")) {
        let highlighted = this.SpanLine(line, offset)

        let div = document.createElement('div')
        div.innerHTML = this.IsWhiteSpace(line) ? '<br>' : highlighted.text
        this.highlightBox.appendChild(div)

        offset += line.length + 1
        spans.push(...highlighted.spans)
    }

    this.spans = spans
    this.FixHeight()
}

Markup.prototype.GetText = function() {
    return this.editableBox.value
}

Markup.prototype.SetText = function(text) {
    this.editableBox.value = text
    this.Highlight()
}
