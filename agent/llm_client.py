from config import global_config as config


async def get_llm_response(messages, tools=None, tool_choice="auto"):
    try:
        if tools:
            response = await config.aclient.chat.completions.create(
                model=config.OLLAMA_MODEL,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=0.1,
            )
        # else:
        #     response = await config.aclient.chat.completions.create(
        #         model=config.OLLAMA_MODEL,
        #         messages=messages,
        #         temperature=0.7,  # Slightly higher for summarization
        #     )
        return response.choices[0].message
    except Exception as e:
        print(f"Error communicating with LLM: {e}")

        return {
            "role": "assistant",
            "content": f"Sorry, I encountered an error trying to process your request: {e}",
        }
