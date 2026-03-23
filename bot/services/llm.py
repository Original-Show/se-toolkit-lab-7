import json
import sys
from openai import AsyncOpenAI
from config import settings
from services.lms import lms_client

client = AsyncOpenAI(
    api_key=settings.llm_api_key,
    base_url=settings.llm_api_base_url
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "List of labs and tasks",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Enrolled students and groups",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Score distribution (4 buckets)",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}},
                "required": ["lab"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Per-task averages and attempt counts",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}},
                "required": ["lab"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Submissions per day",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}},
                "required": ["lab"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Per-group scores and student counts",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}},
                "required": ["lab"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Top N learners by score",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return (default 5)"}
                },
                "required": ["lab"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Completion rate percentage",
            "parameters": {
                "type": "object",
                "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}},
                "required": ["lab"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Refresh data from autochecker",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

async def execute_tool(name: str, args: dict):
    try:
        if name == "get_items": return await lms_client.get_items_raw()
        if name == "get_learners": return await lms_client.get_learners_raw()
        if name == "get_scores": return await lms_client.get_scores_raw(args.get("lab"))
        if name == "get_pass_rates": return await lms_client.get_pass_rates_raw(args.get("lab"))
        if name == "get_timeline": return await lms_client.get_timeline_raw(args.get("lab"))
        if name == "get_groups": return await lms_client.get_groups_raw(args.get("lab"))
        if name == "get_top_learners": return await lms_client.get_top_learners_raw(args.get("lab"), args.get("limit", 5))
        if name == "get_completion_rate": return await lms_client.get_completion_rate_raw(args.get("lab"))
        if name == "trigger_sync": return await lms_client.trigger_sync_raw()
    except Exception as e:
        return {"error": str(e)}
    return {"error": f"Unknown tool: {name}"}

async def route_intent(user_text: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant for the LMS system. Answer questions using the provided tools. Be friendly and clear. For fallback like 'hello', 'asdfgh', tell them concisely what you can do. Always format the answers nicely."},
        {"role": "user", "content": user_text}
    ]

    for step in range(10): # Max 10 turns
        response = await client.chat.completions.create(
            model=settings.llm_api_model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            # We must append the assistant's message, including tool_calls
            messages.append(message)
            tool_count = 0
            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                print(f"[tool] LLM called: {fn_name}({fn_args})", file=sys.stderr)
                
                result = await execute_tool(fn_name, fn_args)
                
                if isinstance(result, list):
                    print(f"[tool] Result: {len(result)} items", file=sys.stderr)
                else:
                    print(f"[tool] Result: {str(result)[:50]}...", file=sys.stderr)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": json.dumps(result)
                })
                tool_count += 1
            print(f"[summary] Feeding {tool_count} tool results back to LLM", file=sys.stderr)
            continue
        else:
            if message.content:
                return message.content
            return "Got empty response from LLM."
    return "Error: Exceeded reasoning steps."
