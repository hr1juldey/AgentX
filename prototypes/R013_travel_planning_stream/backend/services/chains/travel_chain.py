# =============================================================================
# AGENTX R013 - Travel Planning Chain
# =============================================================================
# Sequential chain of specialized travel signatures
# =============================================================================

import logging

import dspy
from services.search_service import search_travel
from services.signatures.destination import DiscoverDestination, GetDestinationInfo
from services.signatures.itinerary import PlanItinerary
from services.signatures.lodging import PlanLodging
from services.signatures.transport import PlanTransport

logger = logging.getLogger(__name__)


# Search tool for DSPy (sync wrapper for async search)
def travel_search_tool(query: str) -> str:
    """Synchronous wrapper for async search - used by DSPy sync mode."""
    import asyncio

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(search_travel(query))


# Async search tool for DSPy async mode
async def travel_search_tool_async(query: str) -> str:
    """Async search tool - used by DSPy async mode."""
    return await search_travel(query)


class TravelPlanningChain:
    """Chain of specialized travel signatures."""

    def __init__(self) -> None:
        """Initialize chain with all specialized modules."""
        self.discover = dspy.Predict(DiscoverDestination)
        self.get_info = dspy.Predict(GetDestinationInfo)
        self.plan_itinerary = dspy.Predict(PlanItinerary)
        self.plan_transport = dspy.Predict(PlanTransport)
        self.plan_lodging = dspy.Predict(PlanLodging)

    async def plan_full_trip(self, question: str, budget: str, group_size: str) -> dict:
        """Execute full planning chain using DSPy async mode.

        Args:
            question: User's travel question
            budget: Budget constraint
            group_size: Number of people

        Returns:
            Dictionary with destination, info, itinerary, transport, lodging
        """
        # Step 1: Discover destination (use acall for async DSPy)
        dest_result = await self.discover.acall(question=question)
        destination = dest_result.destination

        # Step 2: Get current info
        info_result = await self.get_info.acall(destination=destination)

        # Step 3: Plan itinerary
        itinerary_result = await self.plan_itinerary.acall(
            destination=destination, days="7", interests=question
        )

        # Step 4: Plan transport
        transport_result = await self.plan_transport.acall(
            destination=destination, budget=budget, group_size=group_size
        )

        # Step 5: Plan lodging
        lodging_result = await self.plan_lodging.acall(
            destination=destination, budget=budget, group_size=group_size
        )

        return {
            "destination": destination,
            "info": info_result.info,
            "itinerary": itinerary_result.itinerary,
            "transport": transport_result.transport_options,
            "lodging": lodging_result.lodging_options,
        }
