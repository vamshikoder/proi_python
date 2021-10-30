from PyQt5.QtWidgets import (
    QPlainTextEdit,
    QTextEdit,
    QWidget,
)
from PyQt5.QtCore import QRect, Qt, QRegExp
from PyQt5.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QPainter,
    QSyntaxHighlighter,
    QTextFormat,
    QTextCharFormat,
    QTextDocument,
)

import globals


class PCodeOverview(QPlainTextEdit):
    class PNumberBar(QWidget):
        def __init__(self, editor):
            QWidget.__init__(self, editor)

            self.editor = editor

            # * updating the width initially to solve the overlay issue
            self.updateWidth()
            self.editor.blockCountChanged.connect(self.updateWidth)
            self.editor.updateRequest.connect(self.updateContents)
            self.font = QFont()
            self.number_bar_color = QColor("#e8e8e8")

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.fillRect(event.rect(), self.number_bar_color)

            block = self.editor.firstVisibleBlock()

            # Iterate over all visible text blocks in the document.
            while block.isValid():
                block_number = block.blockNumber()
                block_top = (
                    self.editor.blockBoundingGeometry(block)
                    .translated(self.editor.contentOffset())
                    .top()
                )

                # Check if the position of the block is out side of the visible area.
                if not block.isVisible() or block_top >= event.rect().bottom():
                    break

                # We want the line number for the selected line to be bold.
                if block_number == self.editor.textCursor().blockNumber():
                    self.font.setBold(True)
                    painter.setPen(QColor("#000000"))
                else:
                    self.font.setBold(False)
                    painter.setPen(QColor("#717171"))
                painter.setFont(self.font)

                # Draw the line number right justified at the position of the line.
                paint_rect = QRect(
                    0, block_top, self.width(), self.editor.fontMetrics().height()
                )
                painter.drawText(paint_rect, Qt.AlignRight, str(block_number + 1))

                block = block.next()

            painter.end()

            QWidget.paintEvent(self, event)

        def getWidth(self):
            count = self.editor.blockCount()
            width = self.fontMetrics().width(str(count))
            return width

        def updateWidth(self):
            width = self.getWidth()
            # * adding initial spacing to the line numbers (on the left side)
            width += 6
            if self.width() != width:
                self.setFixedWidth(width)
                self.editor.setViewportMargins(width, 0, 0, 0)

        def updateContents(self, rect, scroll):
            if scroll:
                self.scroll(0, scroll)
            else:
                self.update(0, rect.y(), self.width(), rect.height())

            if rect.contains(self.editor.viewport().rect()):
                font_size = self.editor.currentCharFormat().font().pointSize()
                self.font.setPointSize(font_size)
                self.font.setStyle(QFont.StyleNormal)
                self.updateWidth()

    def __init__(
        self,
        syntax_highlighter=None,
    ):
        super(PCodeOverview, self).__init__()

        # * setting font of the editor
        self.setFont((QFont(globals.DEFAULT_FONT_BOLD, 10)))
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        # * setting Tab space to "4 spaces"
        self.setTabStopDistance(QFontMetricsF(self.font()).horizontalAdvance(" ") * 4)

        # * Make the editor read only
        self.setReadOnly(False)

        self.number_bar = self.PNumberBar(self)

        self.current_line_number = None
        self.currentLineColor = self.palette().alternateBase()
        self.cursorPositionChanged.connect(self.highligtCurrentLine)
        self.debug_text()

        # if syntax_highlighter is not None:  # add highlighter to textdocument
        self.highlighter = PSyntaxHighlighter(self.document())

    def debug_text(self):
        """
        adds a simple python script to the editor
        """
        demofile = open("demo_python_pgm.txt", "r")
        for line in demofile.readlines():
            self.appendPlainText(line.removesuffix("\n"))

        # self.setPlainText(str(*demofile.readlines()))

    def resizeEvent(self, *e):
        # if self.DISPLAY_LINE_NUMBERS:  # resize number_bar widget
        cr = self.contentsRect()
        rec = QRect(cr.left(), cr.top(), self.number_bar.getWidth(), cr.height())
        self.number_bar.setGeometry(rec)

        QPlainTextEdit.resizeEvent(self, *e)

    def highligtCurrentLine(self):
        new_current_line_number = self.textCursor().blockNumber()
        if new_current_line_number != self.current_line_number:
            self.current_line_number = new_current_line_number
            hi_selection = QTextEdit.ExtraSelection()
            hi_selection.format.setBackground(self.currentLineColor)
            hi_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection()
            self.setExtraSelections([hi_selection])


def format(color, style=""):
    """Return a QTextCharFormat with the given attributes."""
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if "bold" in style:
        _format.setFontWeight(QFont.Bold)
    if "italic" in style:
        _format.setFontItalic(True)

    return _format


class PSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language."""

    # * Syntax styles that can be shared by all languages
    STYLES = {
        "keyword": format("blue"),
        "operator": format("red"),
        "brace": format("darkGray"),
        "defclass": format("black", "bold"),
        "string": format("magenta"),
        "string2": format("darkMagenta"),
        "comment": format("darkGreen", "italic"),
        "self": format("black", "italic"),
        "numbers": format("brown"),
    }
    # * Python keywords
    KEYWORDS = [
        "and",
        "assert",
        "break",
        "class",
        "continue",
        "def",
        "del",
        "elif",
        "else",
        "except",
        "exec",
        "finally",
        "for",
        "from",
        "global",
        "if",
        "import",
        "in",
        "is",
        "lambda",
        "not",
        "or",
        "pass",
        "print",
        "raise",
        "return",
        "try",
        "while",
        "yield",
        "None",
        "True",
        "False",
    ]

    # * Python operators
    OPERATORS = [
        "=",
        # Comparison
        "==",
        "!=",
        "<",
        "<=",
        ">",
        ">=",
        # Arithmetic
        "\+",
        "-",
        "\*",
        "/",
        "//",
        "\%",
        "\*\*",
        # In-place
        "\+=",
        "-=",
        "\*=",
        "/=",
        "\%=",
        # Bitwise
        "\^",
        "\|",
        "\&",
        "\~",
        ">>",
        "<<",
    ]

    # * Python braces
    BRACES = [
        "\{",
        "\}",
        "\(",
        "\)",
        "\[",
        "\]",
    ]

    def __init__(self, parent: QTextDocument) -> None:
        super().__init__(parent)

        # Multi-line strings (expression, flag, style)
        self.tri_single = (QRegExp("'''"), 1, self.STYLES["string2"])
        self.tri_double = (QRegExp('"""'), 2, self.STYLES["string2"])

        rules = []

        # Keyword, operator, and brace rules
        rules += [
            (r"\b%s\b" % w, 0, self.STYLES["keyword"])
            for w in PSyntaxHighlighter.KEYWORDS
        ]
        rules += [
            (r"%s" % o, 0, self.STYLES["operator"])
            for o in PSyntaxHighlighter.OPERATORS
        ]
        rules += [
            (r"%s" % b, 0, self.STYLES["brace"]) for b in PSyntaxHighlighter.BRACES
        ]

        # All other rules
        rules += [
            # 'self'
            (r"\bself\b", 0, self.STYLES["self"]),
            # 'def' followed by an identifier
            (r"\bdef\b\s*(\w+)", 1, self.STYLES["defclass"]),
            # 'class' followed by an identifier
            (r"\bclass\b\s*(\w+)", 1, self.STYLES["defclass"]),
            # Numeric literals
            (r"\b[+-]?[0-9]+[lL]?\b", 0, self.STYLES["numbers"]),
            (r"\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b", 0, self.STYLES["numbers"]),
            (
                r"\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b",
                0,
                self.STYLES["numbers"],
            ),
            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.STYLES["string"]),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.STYLES["string"]),
            # From '#' until a newline
            (r"#[^\n]*", 0, self.STYLES["comment"]),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        self.triple_quoutes_within_strings = []
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)
            if index >= 0:
                # if there is a string we check
                # if there are some triple quotes within the string
                # they will be ignored if they are matched again
                inner_index = self.tri_single[0].indexIn(text, index + 1)
                if (
                    expression.pattern()
                    in [
                        r'"[^"\\]*(\\.[^"\\]*)*"',
                        r"'[^'\\]*(\\.[^'\\]*)*'",
                    ]
                    and inner_index != -1
                ):
                    # if inner_index == -1:
                    # inner_index = self.tri_double[0].indexIn(text, index + 1)

                    # if inner_index != -1:
                    # else:
                    triple_quote_indexes = range(inner_index, inner_index + 3)
                    self.triple_quoutes_within_strings.extend(triple_quote_indexes)

            while index >= 0:
                # skipping triple quotes within strings
                if index in self.triple_quoutes_within_strings:
                    index += 1
                    expression.indexIn(text, index)
                    continue

                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        # in_multiline = self.match_multiline(text, *self.tri_single)
        # if not in_multiline:
        # in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # * If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # * Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # * skipping triple quotes within strings
            if start in self.triple_quoutes_within_strings:
                return False
            # * Move past this match
            add = delimiter.matchedLength()

        # * As long as there's a delimiter match on this line...
        while start >= 0:
            # * Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # * Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # * No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # * Apply formatting
            self.setFormat(start, length, style)
            # * Look for the next match
            start = delimiter.indexIn(text, start + length)

        # * Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
