import asyncio
import base64
import os
import pytest
from browser_use.browser.context import (
    BrowserContext,
    BrowserContextConfig,
)
from browser_use.browser.views import (
    BrowserError,
    BrowserState,
)
from browser_use.dom.views import (
    DOMElementNode,
)
from unittest.mock import (
    AsyncMock,
    MagicMock,
    Mock,
)


def test_is_url_allowed():
    """
    Test the _is_url_allowed method to verify that it correctly checks URLs against
    the allowed domains configuration.
    Scenario 1: When allowed_domains is None, all URLs should be allowed.
    Scenario 2: When allowed_domains is a list, only URLs matching the allowed domain(s) are allowed.
    Scenario 3: When the URL is malformed, it should return False.
    """
    dummy_browser = Mock()
    dummy_browser.config = Mock()
    config1 = BrowserContextConfig(allowed_domains=None)
    context1 = BrowserContext(browser=dummy_browser, config=config1)
    assert context1._is_url_allowed("http://anydomain.com") is True
    assert context1._is_url_allowed("https://anotherdomain.org/path") is True
    allowed = ["example.com", "mysite.org"]
    config2 = BrowserContextConfig(allowed_domains=allowed)
    context2 = BrowserContext(browser=dummy_browser, config=config2)
    assert context2._is_url_allowed("http://example.com") is True
    assert context2._is_url_allowed("http://sub.example.com/path") is True
    assert context2._is_url_allowed("http://notexample.com") is False
    assert context2._is_url_allowed("https://mysite.org/page") is True
    assert context2._is_url_allowed("http://example.com:8080") is True
    assert context2._is_url_allowed("notaurl") is False


def test_convert_simple_xpath_to_css_selector():
    """
    Test that simple XPath expressions are correctly converted to CSS selectors.
    """
    assert BrowserContext._convert_simple_xpath_to_css_selector("") == ""
    xpath = "/html/body/div/span"
    expected = "html > body > div > span"
    result = BrowserContext._convert_simple_xpath_to_css_selector(xpath)
    assert result == expected
    xpath = "/html/body/div[2]/span"
    expected = "html > body > div:nth-of-type(2) > span"
    result = BrowserContext._convert_simple_xpath_to_css_selector(xpath)
    assert result == expected
    xpath = "/ul/li[3]/a[1]"
    expected = "ul > li:nth-of-type(3) > a:nth-of-type(1)"
    result = BrowserContext._convert_simple_xpath_to_css_selector(xpath)
    assert result == expected


def test_get_initial_state():
    """
    Test that verifies a simulated initial state for BrowserContext.
    Monkey-patches _get_initial_state to return a valid BrowserState instance.
    """
    dummy_browser = Mock()
    dummy_browser.config = Mock()
    context = BrowserContext(browser=dummy_browser, config=BrowserContextConfig())
    context._get_initial_state = lambda page=None: BrowserState(
        element_tree=type("DummyElement", (), {"tag_name": "root"})(),
        selector_map={},
        url=page.url if page is not None else "",
        title="",
        tabs=[],
        screenshot="",
        pixels_above=0,
        pixels_below=0,
    )

    class DummyPage:
        url = "http://dummy.com"

    dummy_page = DummyPage()
    state_with_page = context._get_initial_state(page=dummy_page)
    assert state_with_page.url == dummy_page.url
    assert state_with_page.element_tree.tag_name == "root"
    state_without_page = context._get_initial_state()
    assert state_without_page.url == ""


@pytest.mark.asyncio
async def test_execute_javascript():
    """
    Test that execute_javascript calls page.evaluate and returns the correct result.
    The dummy session is updated to include a dummy context with pages.
    """

    class DummyPage:

        async def evaluate(self, script):
            return "dummy_result"

        async def bring_to_front(self):
            pass

        async def wait_for_load_state(self, state=None):
            pass

    dummy_page = DummyPage()
    dummy_session = type("DummySession", (), {})()
    dummy_session.current_page = dummy_page
    dummy_session.context = type("DummyContext", (), {})()
    dummy_session.context.pages = [dummy_page]
    dummy_browser = Mock()
    dummy_browser.config = Mock()
    context = BrowserContext(browser=dummy_browser, config=BrowserContextConfig())
    context.session = dummy_session
    result = await context.execute_javascript("return 1+1")
    assert result == "dummy_result"


@pytest.mark.asyncio
async def test_enhanced_css_selector_for_element():
    """
    Test the _enhanced_css_selector_for_element method returns the correct selector string
    for a dummy DOMElementNode.
    """
    dummy_element = DOMElementNode(
        tag_name="div",
        is_visible=True,
        parent=None,
        xpath="/html/body/div[2]",
        attributes={
            "class": "foo bar",
            "id": "my-id",
            "placeholder": 'some "quoted" text',
            "data-testid": "123",
        },
        children=[],
    )
    actual_selector = BrowserContext._enhanced_css_selector_for_element(
        dummy_element, include_dynamic_attributes=True
    )
    expected_selector = 'html > body > div:nth-of-type(2).foo.bar[id="my-id"][placeholder*="some \\"quoted\\" text"][data-testid="123"]'
    assert (
        actual_selector == expected_selector
    ), f"Expected {expected_selector}, but got {actual_selector}"


@pytest.mark.asyncio
async def test_get_scroll_info():
    """
    Test that the get_scroll_info method computes the correct scroll information.
    """

    class DummyPage:

        async def evaluate(self, script):
            if "window.scrollY" in script:
                return 100
            elif "window.innerHeight" in script:
                return 500
            elif "document.documentElement.scrollHeight" in script:
                return 1200
            return None

    dummy_page = DummyPage()
    dummy_session = type("DummySession", (), {})()
    dummy_session.current_page = dummy_page
    dummy_session.context = type("DummyContext", (), {})()
    dummy_session.context.pages = [dummy_page]
    dummy_browser = Mock()
    dummy_browser.config = Mock()
    context = BrowserContext(browser=dummy_browser, config=BrowserContextConfig())
    context.session = dummy_session
    pixels_above, pixels_below = await context.get_scroll_info(dummy_page)
    assert pixels_above == 100, f"Expected 100 pixels above, got {pixels_above}"
    assert pixels_below == 600, f"Expected 600 pixels below, got {pixels_below}"


@pytest.mark.asyncio
async def test_reset_context():
    """
    Test that reset_context closes all tabs and, when simulating the creation of a new page and state,
    returns an initial BrowserState with empty URL and a root element.
    """

    class DummyPage:

        def __init__(self, url="http://dummy.com"):
            self.url = url
            self.closed = False

        async def close(self):
            self.closed = True

        async def wait_for_load_state(self, state=None):
            pass

        async def evaluate(self, script):
            return ""

        async def bring_to_front(self):
            pass

    class DummyContext:

        def __init__(self):
            self.pages = []

        async def new_page(self):
            new_page = DummyPage(url="")
            self.pages.append(new_page)
            return new_page

    dummy_context = DummyContext()
    page1 = DummyPage(url="http://page1.com")
    page2 = DummyPage(url="http://page2.com")
    dummy_context.pages.extend([page1, page2])
    dummy_session = type("DummySession", (), {})()
    dummy_session.context = dummy_context
    dummy_session.current_page = page1
    dummy_session.cached_state = None
    dummy_browser = Mock()
    dummy_browser.config = Mock()
    context = BrowserContext(browser=dummy_browser, config=BrowserContextConfig())
    context.session = dummy_session
    await context.reset_context()
    assert page1.closed is True
    assert page2.closed is True
    dummy_context.pages.clear()
    new_page = await context._get_current_page(dummy_session)
    dummy_session.current_page = new_page
    assert new_page.url == ""

    async def dummy_update_state(focus_element=-1):
        return BrowserState(
            element_tree=type("DummyElement", (), {"tag_name": "root"})(),
            selector_map={},
            url="",
            title="",
            tabs=[],
            screenshot="",
            pixels_above=0,
            pixels_below=0,
        )

    context._update_state = dummy_update_state
    state = await context.get_state()
    assert isinstance(state, BrowserState)
    assert state.url == ""
    assert state.element_tree.tag_name == "root"


@pytest.mark.asyncio
async def test_take_screenshot():
    """
    Test that take_screenshot returns a base64 encoded screenshot string.
    The dummy session is updated with a dummy context and page.
    """

    class DummyPage:

        async def screenshot(self, full_page, animations):
            assert full_page is True, "full_page parameter was not correctly passed"
            assert (
                animations == "disabled"
            ), "animations parameter was not correctly passed"
            return b"test"

        async def bring_to_front(self):
            pass

        async def wait_for_load_state(self, state=None):
            pass

    dummy_page = DummyPage()
    dummy_session = type("DummySession", (), {})()
    dummy_session.current_page = dummy_page
    dummy_session.context = type("DummyContext", (), {})()
    dummy_session.context.pages = [dummy_page]
    dummy_browser = Mock()
    dummy_browser.config = Mock()
    context = BrowserContext(browser=dummy_browser, config=BrowserContextConfig())
    context.session = dummy_session
    result = await context.take_screenshot(full_page=True)
    expected = base64.b64encode(b"test").decode("utf-8")
    assert result == expected, f"Expected {expected}, but got {result}"


@pytest.mark.asyncio
async def test_refresh_page_behavior():
    """
    Test that refresh_page triggers reload() and wait_for_load_state on the dummy page.
    The dummy session is updated with a dummy context and page.
    """

    class DummyPage:

        def __init__(self):
            self.reload_called = False
            self.wait_for_load_state_called = False

        async def reload(self):
            self.reload_called = True

        async def wait_for_load_state(self, state=None):
            self.wait_for_load_state_called = True

        async def bring_to_front(self):
            pass

    dummy_page = DummyPage()
    dummy_session = type("DummySession", (), {})()
    dummy_session.current_page = dummy_page
    dummy_session.context = type("DummyContext", (), {})()
    dummy_session.context.pages = [dummy_page]
    dummy_browser = Mock()
    dummy_browser.config = Mock()
    context = BrowserContext(browser=dummy_browser, config=BrowserContextConfig())
    context.session = dummy_session
    await context.refresh_page()
    assert dummy_page.reload_called is True, "Expected the page to call reload()"
    assert (
        dummy_page.wait_for_load_state_called is True
    ), "Expected the page to call wait_for_load_state()"


@pytest.mark.asyncio
async def test_remove_highlights_failure():
    """
    Test that remove_highlights handles exceptions and does not propagate errors.
    """

    class DummyPage:

        async def evaluate(self, script):
            raise Exception("dummy error")

    dummy_page = DummyPage()
    dummy_session = type("DummySession", (), {})()
    dummy_session.current_page = dummy_page
    dummy_session.context = type("DummyContext", (), {})()
    dummy_browser = Mock()
    dummy_browser.config = Mock()
    context = BrowserContext(browser=dummy_browser, config=BrowserContextConfig())
    context.session = dummy_session
    try:
        await context.remove_highlights()
    except Exception as e:
        pytest.fail(f"remove_highlights raised an exception: {e}")


@pytest.mark.asyncio
async def test_is_file_uploader():
    """
    Test the is_file_uploader method for various DOMElementNode scenarios:
    - An input element with type file should be detected as a file uploader.
    - An input element with type text should not be detected as a file uploader.
    - A parent element containing a child that is a file uploader should be detected as a file uploader.
    """
    dummy_browser = Mock()
    dummy_browser.config = Mock()
    context = BrowserContext(browser=dummy_browser, config=BrowserContextConfig())
    file_input = DOMElementNode(
        tag_name="input",
        is_visible=True,
        parent=None,
        xpath="/html/body/input[1]",
        attributes={"type": "file"},
        children=[],
    )
    result_file_input = await context.is_file_uploader(file_input)
    assert (
        result_file_input is True
    ), "Expected an input element with type 'file' to be detected as file uploader."
    text_input = DOMElementNode(
        tag_name="input",
        is_visible=True,
        parent=None,
        xpath="/html/body/input[2]",
        attributes={"type": "text"},
        children=[],
    )
    result_text_input = await context.is_file_uploader(text_input)
    assert (
        result_text_input is False
    ), "Expected an input element with type 'text' not to be detected as file uploader."
    file_child = DOMElementNode(
        tag_name="input",
        is_visible=True,
        parent=None,
        xpath="/html/body/div/input[1]",
        attributes={"type": "file"},
        children=[],
    )
    container = DOMElementNode(
        tag_name="div",
        is_visible=True,
        parent=None,
        xpath="/html/body/div[1]",
        attributes={},
        children=[file_child],
    )
    file_child.parent = container
    result_container = await context.is_file_uploader(container)
    assert (
        result_container is True
    ), "Expected a container with a file uploader element to be detected as file uploader."


@pytest.mark.asyncio
async def test_get_cdp_targets_success():
    """
    Test that _get_cdp_targets properly retrieves CDP targets when the CDP session call succeeds.
    This simulates a dummy page with a dummy context that returns predefined targetInfos.
    """
    dummy_cdp_session = AsyncMock()
    dummy_cdp_session.send.return_value = {
        "targetInfos": [{"targetId": "dummy1", "url": "http://test.com"}]
    }
    dummy_cdp_session.detach.return_value = asyncio.sleep(0)

    class DummyPage:
        pass

    dummy_page = DummyPage()
    dummy_context = MagicMock()
    dummy_context.pages = [dummy_page]
    dummy_context.new_cdp_session = AsyncMock(return_value=dummy_cdp_session)
    dummy_page.context = dummy_context
    dummy_session = MagicMock()
    dummy_session.context = dummy_context
    dummy_browser = Mock()
    dummy_browser.config = MagicMock()
    context = BrowserContext(browser=dummy_browser, config=BrowserContextConfig())
    context.session = dummy_session
    targets = await context._get_cdp_targets()
    assert isinstance(targets, list)
    assert targets == [{"targetId": "dummy1", "url": "http://test.com"}]
