"""Contract tests — verify tool registration and input schemas.

T013 [US1]: atlas_start has no parameters
T017 [US2]: atlas_play requires 'word: str'
T024 [US4]: atlas_concede has no parameters
"""

from __future__ import annotations

from fastmcp.client import Client

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def get_tools(client: Client) -> dict[str, dict]:  # type: ignore[type-arg]
    """Return a dict of tool_name -> tool_info from the server."""
    tools_result = await client.list_tools()
    return {t.name: t for t in tools_result}


# ---------------------------------------------------------------------------
# T013 [US1]: atlas_start schema
# ---------------------------------------------------------------------------


class TestAtlasStartSchema:
    async def test_atlas_start_is_registered(self, atlas_client: Client) -> None:
        tools = await get_tools(atlas_client)
        assert "atlas_start" in tools, "atlas_start tool must be registered"

    async def test_atlas_start_has_no_parameters(self, atlas_client: Client) -> None:
        tools = await get_tools(atlas_client)
        tool = tools["atlas_start"]
        props = tool.inputSchema.get("properties", {})
        assert props == {}, f"atlas_start must have no parameters, got: {props}"

    async def test_atlas_start_has_no_required_fields(self, atlas_client: Client) -> None:
        tools = await get_tools(atlas_client)
        tool = tools["atlas_start"]
        required = tool.inputSchema.get("required", [])
        assert required == [], f"atlas_start must have no required fields, got: {required}"


# ---------------------------------------------------------------------------
# T017 [US2]: atlas_play schema
# ---------------------------------------------------------------------------


class TestAtlasPlaySchema:
    async def test_atlas_play_is_registered(self, atlas_client: Client) -> None:
        tools = await get_tools(atlas_client)
        assert "atlas_play" in tools, "atlas_play tool must be registered"

    async def test_atlas_play_has_word_parameter(self, atlas_client: Client) -> None:
        tools = await get_tools(atlas_client)
        tool = tools["atlas_play"]
        props = tool.inputSchema.get("properties", {})
        assert "word" in props, f"atlas_play must have 'word' parameter, got: {list(props)}"
        assert props["word"].get("type") == "string", "atlas_play 'word' must be type string"

    async def test_atlas_play_word_is_required(self, atlas_client: Client) -> None:
        tools = await get_tools(atlas_client)
        tool = tools["atlas_play"]
        required = tool.inputSchema.get("required", [])
        assert "word" in required, f"'word' must be required in atlas_play, got: {required}"


# ---------------------------------------------------------------------------
# T024 [US4]: atlas_concede schema
# ---------------------------------------------------------------------------


class TestAtlasConcedeSchema:
    async def test_atlas_concede_is_registered(self, atlas_client: Client) -> None:
        tools = await get_tools(atlas_client)
        assert "atlas_concede" in tools, "atlas_concede tool must be registered"

    async def test_atlas_concede_has_no_parameters(self, atlas_client: Client) -> None:
        tools = await get_tools(atlas_client)
        tool = tools["atlas_concede"]
        props = tool.inputSchema.get("properties", {})
        assert props == {}, f"atlas_concede must have no parameters, got: {props}"
