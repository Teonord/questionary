# -*- coding: utf-8 -*-
import asyncio

import prompt_toolkit
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

from questionary import prompt
from questionary.prompts import prompt_by_name
from questionary.utils import is_prompt_toolkit_3

_prompt_toolkit_version = [int(v) for v in prompt_toolkit.VERSION]


class KeyInputs:
    DOWN = "\x1b[B"
    UP = "\x1b[A"
    LEFT = "\x1b[D"
    RIGHT = "\x1b[C"
    ENTER = "\r"
    ESCAPE = "\x1b"
    CONTROLC = "\x03"
    CONTROLN = "\x0e"
    CONTROLP = "\x10"
    BACK = "\x7f"
    SPACE = " "
    TAB = "\x09"
    ONE = "1"
    TWO = "2"
    THREE = "3"


def feed_cli_with_input(_type, message, texts, sleep_time=1, **kwargs):
    """
    Create a Prompt, feed it with the given user input and return the CLI
    object.

    You an provide multiple texts, the feeder will async sleep for `sleep_time`

    This returns a (result, Application) tuple.
    """

    if not isinstance(texts, list):
        texts = [texts]

    inp = create_pipe_input()

    if (
        _prompt_toolkit_version[0] <= 3
        and _prompt_toolkit_version[1] == 0
        and _prompt_toolkit_version[2] < 29
    ):
        try:
            return _create_input(_type, inp, kwargs, message, sleep_time, texts)
        finally:
            inp.close()
    else:
        with create_pipe_input() as inp:
            return _create_input(_type, inp, kwargs, message, sleep_time, texts)


def _create_input(_type, inp, kwargs, message, sleep_time, texts):
    prompter = prompt_by_name(_type)
    application = prompter(message, input=inp, output=DummyOutput(), **kwargs)
    if is_prompt_toolkit_3():
        loop = asyncio.new_event_loop()
        future_result = loop.create_task(application.unsafe_ask_async())

        for i, text in enumerate(texts):
            # noinspection PyUnresolvedReferences
            inp.send_text(text)

            if i != len(texts) - 1:
                loop.run_until_complete(asyncio.sleep(sleep_time))
        result = loop.run_until_complete(future_result)
    else:
        for text in texts:
            inp.send_text(text)
        result = application.unsafe_ask()
    return result, application


def patched_prompt(questions, text, **kwargs):
    """Create a prompt where the input and output are predefined."""

    inp = create_pipe_input()

    try:
        # noinspection PyUnresolvedReferences
        inp.send_text(text)
        result = prompt(questions, input=inp, output=DummyOutput(), **kwargs)
        return result

    finally:
        inp.close()
