from typing import Any, Generator

import streamlit as st

from services.orchestrator import UIHandler


class StreamlitUIHandler(UIHandler):
    """Implementation of UIHandler for the Streamlit web interface."""

    def on_stage_start(self, stage_idx: int, message: str) -> Any:
        # st.status returns a container that can be updated
        # We expand Stage 3 (Summary) by default to show streaming
        return st.status(message, expanded=(stage_idx == 3))

    def on_stage_update(self, handle: Any, message: str, state: str) -> None:
        # handle is expected to be an st.status container
        handle.update(label=message, state=state)

    def handle_stream(self, stream: Generator[str, None, None]) -> str:
        # st.write_stream renders tokens and returns the full text
        return st.write_stream(stream)

    def render_skeletons(self, stage_idx: int) -> None:
        from ui.styles import render_skeletons

        render_skeletons(stage_idx)
