"""Allure tweaks and whistles"""

import allure
import pytest
import wrapt
from allure_commons.types import AttachmentType
from selene import browser


def validation(title):
    """Step which raises AssertionError and captures screenshot on fail"""

    is_fnc = callable(title)
    real_title = title.__name__ if is_fnc else title
    step = allure.step(real_title)

    def _check(fnc):
        def _real_check(*args, **kwargs):
            with step:
                try:
                    return fnc(*args, **kwargs)
                except Exception as tme:
                    allure.attach.file(browser.take_screenshot(), name="Screenshot", attachment_type=AttachmentType.PNG)
                    raise AssertionError(real_title) from tme

        return _real_check

    if is_fnc:
        return _check(title)

    return _check


def tags(*applied_tags: str):
    """Let use :fnc:`pytest.mark` in way:

        ``@tag("smoke")...`` or ``@tags("smoke", "draft")``
    """

    @wrapt.decorator
    def _tags(wrapped, instance=None, args=(), kwargs=None):
        del instance
        marks = pytest.mark
        fnc = wrapped
        for _tag in applied_tags:
            actual_mark = getattr(marks, _tag)
            fnc = actual_mark(fnc)
        return fnc(*args, **kwargs)

    return _tags
