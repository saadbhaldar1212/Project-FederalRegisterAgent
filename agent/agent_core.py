import json

from datetime import date

from agent.llm_client import get_llm_response
from agent.tool_executor import query_federal_registry_db

from config import global_config as config


AVAILABLE_TOOLS = {
    "query_federal_registry_db": query_federal_registry_db,
}


async def process_user_query(user_query: str, chat_history: list = None):

    current_date_str = date.today().strftime("%Y-%m-%d")

    if chat_history is None:
        chat_history = []

    messages = [
        {
            "role": "system",
            "content": config.SYSTEM_PROMPT.format(current_date=current_date_str),
        }
    ]
    messages.extend(chat_history)  # Add past exchanges if any
    messages.append({"role": "user", "content": user_query})

    MAX_TOOL_CALLS_PER_TURN = 3  # Safety break
    tool_calls_count = 0

    while tool_calls_count < MAX_TOOL_CALLS_PER_TURN:
        # print(f"\nSending to LLM (Turn {tool_calls_count + 1}): {messages[-1]}")
        llm_response_message = await get_llm_response(
            messages, tools=config.FEDERAL_REGISTRY_TOOL_SCHEMA, tool_choice="auto"
        )
        # print(f"LLM Raw Response: {llm_response_message}")

        if not llm_response_message:
            return "Sorry, I couldn't connect to the language model right now."

        # Check for tool calls
        if (
            hasattr(llm_response_message, "tool_calls")
            and llm_response_message.tool_calls
        ):
            tool_calls = llm_response_message.tool_calls
            messages.append(llm_response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args_json = tool_call.function.arguments
                print(f"Using tool: {function_name}")

                if function_name in AVAILABLE_TOOLS:
                    function_to_call = AVAILABLE_TOOLS[function_name]
                    try:
                        function_args = json.loads(function_args_json)

                        tool_output_json = await function_to_call(**function_args)
                    except json.JSONDecodeError:
                        tool_output_json = json.dumps(
                            {"error": "Invalid JSON arguments from LLM."}
                        )
                    except Exception as e:
                        print(f"Error executing tool {function_name}: {e}")
                        tool_output_json = json.dumps(
                            {"error": f"Error executing tool: {str(e)}"}
                        )

                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": tool_output_json,
                        }
                    )
                else:
                    print(f"Error: LLM tried to call unknown tool: {function_name}")
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(
                                {
                                    "error": f"Tool '{function_name}' not found or not permitted."
                                }
                            ),
                        }
                    )
            tool_calls_count += 1

        else:

            final_answer = llm_response_message.content
            # print(f"LLM Final Answer: {final_answer}")

            chat_history.append({"role": "user", "content": user_query})
            chat_history.append({"role": "assistant", "content": final_answer})
            return final_answer

    return "I tried to use my tools to find an answer, but it took too many steps. Could you please rephrase your question or be more specific?"
