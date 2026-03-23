# Development Plan for se-toolkit-lab-7 Telegram Bot

This plan details the architecture and strategy for building the Telegram bot across the four core tasks.

## Task 1: Scaffolding and Architecture
We establish a clean, modular structure. The entry point `bot.py` handles parsing arguments. If `--test` is passed, it uses a mock dispatcher or directly calls the handlers, passing the input text, and writes the string response to standard output. If not testing, it starts the `aiogram` event loop. Handlers are isolated in the `handlers/` directory, and avoid direct dependency on Telegram's network layer so they remain testable. Dependencies are managed via `uv` in `pyproject.toml`.

## Task 2: Backend Integration
We will configure `httpx.AsyncClient` in the `services/` layer to interact with the LMS FastApi backend, using the `LMS_API_BASE_URL` and `LMS_API_KEY` defined in our environment variables. Typical commands like `/health`, `/labs`, and `/scores` will decode the arguments, make the appropriate REST API call to the backend, handle missing or down-services with a friendly error message, and format the JSON response into human-readable text for the Telegram user.

## Task 3: Intent Routing via LLM
For arbitrary text inputs, we will integrate with the Qwen Code LLM API. The LLM will receive a system prompt containing the available backend endpoints as tool descriptions. We will implement function calling so the LLM can decide which endpoint to query based on user intent, orchestrate the data fetch, and synthesize a natural language response back to the user.

## Task 4: Deployment
We will package the bot in a lightweight Docker image using `python:3.12-slim`. We will add the bot service to the existing `docker-compose.yml`, mount the `.env.bot.secret` file, and deploy it to the VM so it runs alongside the LMS backend.
