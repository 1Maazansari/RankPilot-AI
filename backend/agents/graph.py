"""
BrandVizi LangGraph Orchestration.

This module builds the complete BrandVizi AI agent workflow
using LangGraph's StateGraph.

Workflow:

    START
      ↓
Technical SEO Agent
      ↓
Content Intelligence Agent
      ↓
AEO/GEO Agent
      ↓
Validation
      ↓
     END
"""

from langgraph.graph import END, START, StateGraph

from backend.agents.aeo_geo import aeo_geo_node
from backend.agents.content_intelligence import (
    content_intelligence_node,
)
from backend.agents.state import AgentState
from backend.agents.technical_seo import technical_seo_node
from backend.agents.validation import validation_node


# ============================================================
# GRAPH BUILDER
# ============================================================

def build_agent_graph():
    """
    Build and compile the BrandVizi LangGraph workflow.

    Returns
    -------
    CompiledStateGraph
        Compiled LangGraph workflow ready for invocation.
    """

    # ---------------------------------------------------------
    # 1. Create StateGraph
    # ---------------------------------------------------------

    builder = StateGraph(
        AgentState
    )

    # ---------------------------------------------------------
    # 2. Register specialist agents
    # ---------------------------------------------------------

    builder.add_node(
        "technical_seo",
        technical_seo_node,
    )

    builder.add_node(
        "content_intelligence",
        content_intelligence_node,
    )

    builder.add_node(
        "aeo_geo",
        aeo_geo_node,
    )

    # Validation is a control/verification node,
    # not a fourth intelligence agent.
    builder.add_node(
        "validation",
        validation_node,
    )

    # ---------------------------------------------------------
    # 3. Define workflow edges
    # ---------------------------------------------------------

    builder.add_edge(
        START,
        "technical_seo",
    )

    builder.add_edge(
        "technical_seo",
        "content_intelligence",
    )

    builder.add_edge(
        "content_intelligence",
        "aeo_geo",
    )

    builder.add_edge(
        "aeo_geo",
        "validation",
    )

    builder.add_edge(
        "validation",
        END,
    )

    # ---------------------------------------------------------
    # 4. Compile graph
    # ---------------------------------------------------------

    return builder.compile()


# ============================================================
# COMPILED BRANDVIZI GRAPH
# ============================================================

brandvizi_agent_graph = build_agent_graph()