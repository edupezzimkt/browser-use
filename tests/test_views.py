import pytest
from browser_use.controller.views import (
    ClickElementAction,
    InputTextAction,
    NoParamsAction,
    ScrollAction,
)


def test_no_params_action_ignores_all_input():
    """
    Test that NoParamsAction discards all incoming data.

    This test instantiates NoParamsAction with arbitrary fields and ensures that,
    due to the model validator, the resulting model instance's dict is empty.
    """
    instance = NoParamsAction(foo="bar", extra_field=42)
    assert instance.dict() == {}


def test_click_element_action_defaults():
    """
    Test that ClickElementAction sets proper default values for optional fields when those fields are not provided.
    In this test, only the required 'index' field is provided, and the test confirms that 'xpath' defaults to None and 'right_click' defaults to False.
    """
    instance = ClickElementAction(index=3)
    assert instance.dict() == {"index": 3, "xpath": None, "right_click": False}


def test_scroll_action_defaults_and_value():
    """
    Test that ScrollAction defaults to None when no amount is provided,
    and correctly sets the 'amount' when a value is given.
    """
    default_instance = ScrollAction()
    assert default_instance.dict() == {
        "amount": None
    }, "Expected 'amount' to be None when not provided."
    instance_with_amount = ScrollAction(amount=100)
    assert instance_with_amount.dict() == {
        "amount": 100
    }, "Expected 'amount' to be 100 when provided."


def test_input_text_action_with_optional_field():
    """
    Test that InputTextAction requires 'index' and 'text' and
    correctly handles the optional 'xpath' field, defaulting to None
    when not provided and accepting a custom value when provided.
    """
    instance_default = InputTextAction(index=2, text="sample")
    assert instance_default.dict() == {"index": 2, "text": "sample", "xpath": None}
    instance_with_xpath = InputTextAction(index=2, text="sample", xpath="//input")
    assert instance_with_xpath.dict() == {
        "index": 2,
        "text": "sample",
        "xpath": "//input",
    }
