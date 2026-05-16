"""
Tests for citation handling utilities.
"""
import pytest


def test_deduplicate_sources_removes_duplicates():
    """Test that deduplicate_sources removes duplicate content."""
    from rag.citations import deduplicate_sources
    
    sources = [
        {
            "content": "Hypertension is elevated blood pressure.",
            "metadata": {"title": "Title1", "source": "Source1"}
        },
        {
            "content": "Hypertension is elevated blood pressure.",  # Duplicate
            "metadata": {"title": "Title2", "source": "Source2"}
        },
        {
            "content": "Diabetes is elevated blood sugar.",
            "metadata": {"title": "Title3", "source": "Source3"}
        }
    ]
    
    result = deduplicate_sources(sources)
    
    assert len(result) == 2
    assert result[0]["content"] == "Hypertension is elevated blood pressure."
    assert result[1]["content"] == "Diabetes is elevated blood sugar."


def test_deduplicate_sources_preserves_order():
    """Test that deduplicate_sources preserves first occurrence."""
    from rag.citations import deduplicate_sources
    
    sources = [
        {
            "content": "Content A",
            "metadata": {"title": "First", "source": "Source1"}
        },
        {
            "content": "Content B",
            "metadata": {"title": "Second", "source": "Source2"}
        },
        {
            "content": "Content A",  # Duplicate of first
            "metadata": {"title": "Third", "source": "Source3"}
        }
    ]
    
    result = deduplicate_sources(sources)
    
    assert len(result) == 2
    assert result[0]["metadata"]["title"] == "First"  # First occurrence preserved
    assert result[1]["metadata"]["title"] == "Second"


def test_deduplicate_sources_empty_list():
    """Test deduplicate_sources with empty list."""
    from rag.citations import deduplicate_sources
    
    result = deduplicate_sources([])
    
    assert result == []


def test_deduplicate_sources_no_duplicates():
    """Test deduplicate_sources when all sources are unique."""
    from rag.citations import deduplicate_sources
    
    sources = [
        {"content": "Content A", "metadata": {}},
        {"content": "Content B", "metadata": {}},
        {"content": "Content C", "metadata": {}}
    ]
    
    result = deduplicate_sources(sources)
    
    assert len(result) == 3


def test_deduplicate_sources_handles_empty_content():
    """Test deduplicate_sources with empty content."""
    from rag.citations import deduplicate_sources
    
    sources = [
        {"content": "", "metadata": {"title": "Empty1"}},
        {"content": "Real content", "metadata": {"title": "Real"}},
        {"content": "", "metadata": {"title": "Empty2"}}
    ]
    
    result = deduplicate_sources(sources)
    
    # Empty content should be filtered out
    assert len(result) == 1
    assert result[0]["content"] == "Real content"


def test_format_citations_basic():
    """Test basic citation formatting."""
    from rag.citations import format_citations
    
    sources = [
        {
            "content": "Content 1",
            "metadata": {"title": "Hypertension Overview", "source": "StatPearls"}
        },
        {
            "content": "Content 2",
            "metadata": {"title": "Treatment Guidelines", "source": "StatPearls"}
        }
    ]
    
    result = format_citations(sources)
    
    assert "[1] Hypertension Overview (StatPearls)" in result
    assert "[2] Treatment Guidelines (StatPearls)" in result


def test_format_citations_empty_sources():
    """Test format_citations with empty sources."""
    from rag.citations import format_citations
    
    result = format_citations([])
    
    assert result == ""


def test_format_citations_missing_metadata():
    """Test format_citations with missing metadata fields."""
    from rag.citations import format_citations
    
    sources = [
        {
            "content": "Content",
            "metadata": {}  # Missing title and source
        }
    ]
    
    result = format_citations(sources)
    
    assert "[1] Unknown Title (Unknown Source)" in result


def test_format_citations_partial_metadata():
    """Test format_citations with partial metadata."""
    from rag.citations import format_citations
    
    sources = [
        {
            "content": "Content",
            "metadata": {"title": "Known Title"}  # Missing source
        }
    ]
    
    result = format_citations(sources)
    
    assert "[1] Known Title (Unknown Source)" in result


def test_format_citations_multiple_sources():
    """Test format_citations with multiple sources."""
    from rag.citations import format_citations
    
    sources = [
        {"content": "C1", "metadata": {"title": "T1", "source": "S1"}},
        {"content": "C2", "metadata": {"title": "T2", "source": "S2"}},
        {"content": "C3", "metadata": {"title": "T3", "source": "S3"}}
    ]
    
    result = format_citations(sources)
    
    lines = result.split("\n")
    assert len(lines) == 3
    assert lines[0].startswith("[1]")
    assert lines[1].startswith("[2]")
    assert lines[2].startswith("[3]")


def test_assemble_context_basic():
    """Test basic context assembly."""
    from rag.citations import assemble_context
    
    sources = [
        {"content": "Hypertension is elevated blood pressure.", "metadata": {}},
        {"content": "Treatment includes medications.", "metadata": {}}
    ]
    
    result = assemble_context(sources)
    
    assert "[Source 1]" in result
    assert "Hypertension is elevated blood pressure." in result
    assert "[Source 2]" in result
    assert "Treatment includes medications." in result


def test_assemble_context_empty_sources():
    """Test assemble_context with empty sources."""
    from rag.citations import assemble_context
    
    result = assemble_context([])
    
    assert result == ""


def test_assemble_context_empty_content():
    """Test assemble_context with empty content."""
    from rag.citations import assemble_context
    
    sources = [
        {"content": "", "metadata": {}},
        {"content": "Real content", "metadata": {}},
        {"content": "", "metadata": {}}
    ]
    
    result = assemble_context(sources)
    
    # Should only include non-empty content
    # Note: Source numbering is based on position in list, so "Real content" is Source 2
    assert "[Source 2]" in result
    assert "Real content" in result
    assert result.count("[Source") == 1  # Only one source marker


def test_assemble_context_separator():
    """Test that assemble_context uses correct separator."""
    from rag.citations import assemble_context
    
    sources = [
        {"content": "Content A", "metadata": {}},
        {"content": "Content B", "metadata": {}}
    ]
    
    result = assemble_context(sources)
    
    # Should be separated by double newline
    assert "\n\n" in result


def test_assemble_context_preserves_order():
    """Test that assemble_context preserves source order."""
    from rag.citations import assemble_context
    
    sources = [
        {"content": "First content", "metadata": {}},
        {"content": "Second content", "metadata": {}},
        {"content": "Third content", "metadata": {}}
    ]
    
    result = assemble_context(sources)
    
    # Verify order
    first_pos = result.find("First content")
    second_pos = result.find("Second content")
    third_pos = result.find("Third content")
    
    assert first_pos < second_pos < third_pos


def test_assemble_context_single_source():
    """Test assemble_context with single source."""
    from rag.citations import assemble_context
    
    sources = [
        {"content": "Single content", "metadata": {}}
    ]
    
    result = assemble_context(sources)
    
    assert "[Source 1]" in result
    assert "Single content" in result
    assert "[Source 2]" not in result

# Made with Bob