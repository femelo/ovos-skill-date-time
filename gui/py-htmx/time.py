from __future__ import annotations
from typing import Any, Optional, Dict
from datetime import datetime

from pyhtmx import Div, Span, Style, Link, Script
from pyhtmx_gui.kit import Widget, SessionItem, Page


class FlipClockWidget(Widget):
    _parameters = ("time_string", "date_string")

    def __init__(self, session_data: Optional[Dict[str, Any]] = None):
        super().__init__(name="flip-clock-widget", session_data=session_data or {})

        time_string = session_data.get("time_string", "00:00")
        date_string = session_data.get("date_string", "01/01/1970")

        hours, minutes = time_string.split(":")

        try:
            hour_int = int(hours)
        except ValueError:
            hour_int = 0
        is_day = 6 <= hour_int < 18

        bg_class = "bg-white" if is_day else "bg-gray-900"
        secondary_text = "text-gray-700" if is_day else "text-gray-400"

        def get_text_color(bg: str) -> str:
            return "text-white" if bg in ["bg-black", "bg-gray-800", "bg-gray-900"] else "text-black"

        colon_text_color = "text-black" if is_day else "text-white"

        def build_flip_unit(value: str | None, unit_id: str, animate=False, is_colon=False):
            if is_colon:
                classes = f"block text-[10vw] font-mono font-bold {colon_text_color}"
                return Div(
                    [Span(":", _id=f"{unit_id}-text", _class=classes)],
                    _id=f"flip-{unit_id}",
                    _class=["flex", "items-center", "justify-center", "mx-[0.5vw]"],
                    style={"height": "20vw", "width": "auto"},
                )
            else:
                bg = "bg-black" if not is_day else "bg-gray-800"
                text_color = get_text_color(bg)
                classes = f"block text-[10vw] font-mono font-bold {text_color}"
                if animate:
                    classes += " animate-flip"

                return Div(
                    [Span(value, _id=f"{unit_id}-text", _class=classes)],
                    _id=f"flip-{unit_id}",
                    _class=[
                        "w-[14vw]", "h-[20vw]",
                        bg, "rounded-lg",
                        "flex", "items-center", "justify-center",
                        "shadow-inner", "mx-[1vw]",
                    ],
                )

        self._hour = build_flip_unit(hours, "hours", animate=False)
        self._colon = build_flip_unit(None, "colon", is_colon=True)
        self._minute = build_flip_unit(minutes, "minutes", animate=True)

        self._time_row = Div(
            [self._hour, self._colon, self._minute],
            _class="flex flex-row items-center justify-center",
        )

        self._date = Div(
            inner_content=date_string,
            _id="flip-date",
            _class=f"text-[3vw] {secondary_text} mt-[1vw]",
        )

        self._style = Style("""
        @keyframes flip {
            0%   { transform: rotateX(0); }
            50%  { transform: rotateX(-90deg); }
            100% { transform: rotateX(0); }
        }
        .animate-flip {
            animation: flip 0.6s ease-in-out;
            transform-origin: top;
            display: inline-block;
        }
        """)

        # De klok zelf in kaart-stijl
        self._widget: Div = Div(
            [
                self._style,
                self._time_row,
                self._date,
            ],
            _id="flip-clock-widget",
            _class=[
                "p-[2vw]",
                "flex", "flex-col",
                "items-center", "justify-center",
                bg_class,
                "rounded-2xl",
                "shadow-xl",
            ],
            style={
                "width": "80vw",
                "height": "80vh",
            },
        )

        # Interacties
        self.add_interaction(
            "time_string",
            SessionItem(parameter="time_string", attribute="inner_content", component=self._hour),
        )
        self.add_interaction(
            "time_string",
            SessionItem(parameter="time_string", attribute="inner_content", component=self._minute),
        )
        self.add_interaction(
            "date_string",
            SessionItem(parameter="date_string", attribute="inner_content", component=self._date),
        )


class TimePage(Page):
    def __init__(self, session_data: Optional[Dict[str, Any]] = None):
        super().__init__(name="time-page", session_data=session_data or {})

        flip_clock = FlipClockWidget(session_data=session_data)

        # Achtergrondcontainer met lineaire gradient zoals in homescreen
        background_container = Div(
            [flip_clock.widget],
            _id="carousel-bg",
            _class=[
                "h-full",
                "w-full",
                "flex",
                "flex-col",
                "items-center",
                "justify-center",
            ],
            style={
                "background": (
                    "linear-gradient(to right, rgb(59, 130, 246), rgb(255, 182, 193))"
                ),
                "transition": "background 0.5s ease",
            },
        )

        # Extra CSS en JS zoals bij homescreen (indien relevant)
        style = Link(rel="stylesheet", href="assets/css/carousel.css")
        script = Script(src="assets/js/carousel.js")

        self._page: Div = Div(
            [background_container, style, script],
            _id="time-page",
            _class="flex flex-col",
            style={"width": "100vw", "height": "100vh"},
        )
