# =============================================================================
# AGENTX Delivery Planner - Execution Logic
# =============================================================================
# Async execution of staggered widget delivery
# =============================================================================

import asyncio


class DeliveryExecution:
    """Handles async execution of staggered widget delivery."""

    @staticmethod
    async def deliver_with_delay(
        delivery_plan,
        delivery_callback,
    ) -> None:
        """Execute staggered delivery with async delays.

        Args:
            delivery_plan: The planned delivery schedule
            delivery_callback: Async function to call for each widget delivery
        """
        tasks = []
        for delay, widget in delivery_plan.get_delivery_schedule():
            # Schedule each widget delivery with its delay
            task = asyncio.create_task(
                DeliveryExecution._deliver_after_delay(delay, widget, delivery_callback)
            )
            tasks.append(task)

        # Wait for all deliveries to complete
        await asyncio.gather(*tasks)

    @staticmethod
    async def _deliver_after_delay(
        delay: float,
        widget: dict,
        callback,
    ) -> None:
        """Deliver a single widget after its delay.

        Args:
            delay: Time to wait before delivering
            widget: Widget to deliver
            callback: Callback function to deliver the widget
        """
        await asyncio.sleep(delay)
        await callback(widget)
