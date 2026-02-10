from pyhtmx import Div, Img, Style, Script  # type: ignore
from pyhtmx_gui.kit import Widget, Page
from typing import Optional, Dict, Any


class MatrixClockWidget(Widget):
    def __init__(self, session_data: Optional[Dict[str, Any]] = None):
        super().__init__(name="matrix-clock-widget", session_data=session_data or {})

        self._style = Style("""
        body,html {
            margin: 0; height: 100vh; overflow: hidden; 
            display: flex; justify-content: center; align-items: center; 
            background: white;
        }
        .container {
            position: relative;
            width: 1000px;
            height: auto;
        }
        .background {
            position: absolute;
            top: 50%; left: 50%;
            width: 100%;
            height: auto;
            transform: translate(-50%, -50%) scale(1.25);
            object-fit: cover;
            z-index: 0;
        }
        .matrix {
            position: absolute;
            top: -80px;
            left: 50%;
            transform: translate(-50%);
            display: grid;
            grid-template-columns: repeat(32, 1fr);
            grid-template-rows: repeat(8, 1fr);
            gap: 1.5px;
            width: 450px;
            height: 110px;
            pointer-events: none;
            z-index: 1;
        }
        .pixel {
            width: 12.2px;
            height: 12.2px;
            border-radius: 50%;
            background-color: #222222;
            transition: background-color 0.1s;
        }
        .on {
            background-color: white;
        }
        """)

        self._container = Div(
            [
                Img(src="assets/images/mk1.png", alt="Mark 1", _class="background"),
                Div(
                    [],  # pixels worden via JS aangemaakt
                    _id="matrix",
                    _class="matrix",
                ),
            ],
            _class="container",
        )

        self._script = Script(
            """
            const matrix = document.getElementById('matrix');
            const rows = 8;
            const cols = 32;
            const pixels = [];

            for (let i = 0; i < rows * cols; i++) {
              const pixel = document.createElement('div');
              pixel.classList.add('pixel');
              matrix.appendChild(pixel);
              pixels.push(pixel);
            }

            const font = {
              "0": ["01110","10001","10011","10101","11001","10001","01110"],
              "1": ["00100","01100","00100","00100","00100","00100","01110"],
              "2": ["01110","10001","00001","00110","01000","10000","11111"],
              "3": ["01110","10001","00001","00110","00001","10001","01110"],
              "4": ["00010","00110","01010","10010","11111","00010","00010"],
              "5": ["11111","10000","11110","00001","00001","10001","01110"],
              "6": ["00110","01000","10000","11110","10001","10001","01110"],
              "7": ["11111","00001","00010","00100","01000","01000","01000"],
              "8": ["01110","10001","10001","01110","10001","10001","01110"],
              "9": ["01110","10001","10001","01111","00001","00010","01100"],
              ":": ["00000","00100","00100","00000","00100","00100","00000"],
              " ": ["00000","00000","00000","00000","00000","00000","00000"]
            };

            function renderChar(char) {
              const glyph = font[char] || font[" "];
              const columnData = [];
              for (let i = 0; i < glyph[0].length; i++) {
                const col = Array(rows).fill(0);
                for (let j = 0; j < glyph.length; j++) {
                  col[j + 1] = parseInt(glyph[j][i]);
                }
                columnData.push(col);
              }
              columnData.push(Array(rows).fill(0));
              return columnData;
            }

            function drawBuffer(buffer, xOffset = 0) {
              for (let y = 0; y < rows; y++) {
                for (let x = 0; x < cols; x++) {
                  const index = y * cols + x;
                  const pixel = pixels[index];
                  const col = buffer[x + xOffset];
                  if (col && col[y] === 1) {
                    pixel.classList.add('on');
                  } else {
                    pixel.classList.remove('on');
                  }
                }
              }
            }

            function getTimeString() {
              const now = new Date();
              const hh = String(now.getHours()).padStart(2, "0");
              const mm = String(now.getMinutes()).padStart(2, "0");
              return `${hh}:${mm}`;
            }

            function showTimeThenScrollOnce() {
              const time = getTimeString();
              let buffer = [];
              time.split("").forEach(char => {
                buffer = buffer.concat(renderChar(char));
              });
              const centerOffset = Math.floor((cols - buffer.length) / 2);
              drawBuffer(buffer, -centerOffset);

              setTimeout(() => {
                const scrollBuffer = buffer.concat(Array(cols).fill(Array(rows).fill(0)));
                let offset = 0;
                const scroll = setInterval(() => {
                  drawBuffer(scrollBuffer, offset);
                  offset++;
                  if (offset > scrollBuffer.length - cols) {
                    clearInterval(scroll);
                  }
                }, 100);
              }, 3000);
            }

            const bg = document.querySelector('.background');
            if (bg.complete) {
              showTimeThenScrollOnce();
            } else {
              bg.onload = () => showTimeThenScrollOnce();
            }
            """
        )

        self._widget = Div(
            [
                self._style,
                self._container,
                self._script,
            ],
            _id="matrix-clock-widget",
            _class="w-screen h-screen flex justify-center items-center bg-white",
            style={"width": "100vw", "height": "100vh"},
        )


class MatrixClockPage(Page):
    def __init__(self, session_data: Optional[Dict[str, Any]] = None):
        super().__init__(name="matrix-clock-page", session_data=session_data or {})

        widget = MatrixClockWidget(session_data=session_data)

        self._page = Div(
            [widget._widget],
            _id="matrix-clock-page",
            _class="w-screen h-screen flex justify-center items-center bg-white",
            style={"width": "100vw", "height": "100vh"},
        )
