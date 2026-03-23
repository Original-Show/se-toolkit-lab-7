from services.lms import lms_client

async def health_handler(text: str) -> str:
    return await lms_client.get_health()

async def labs_handler(text: str) -> str:
    return await lms_client.get_labs()

async def scores_handler(text: str) -> str:
    parts = text.split()
    if len(parts) < 2:
        return "Please provide a lab identifier. Example: /scores lab-04"
    return await lms_client.get_scores(parts[1])
