"""
First Claude API call from the journey.
Day 1 — establishes the pattern for all future scripts.
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv


def main() -> None:
    # Load environment variables from .env file
    load_dotenv()

    # Verify the API key was loaded
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not found. Check that .env exists in this folder "
            "and contains: ANTHROPIC_API_KEY=sk-ant-..."
        )

    # Create the client (it auto-reads ANTHROPIC_API_KEY from env)
    client = Anthropic()

    # Send a message to Claude
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "In exactly 3 sentences, explain what an LLM API "
                           "is to a data analyst transitioning into AI engineering.",
            }
        ],
    )

    # Print Claude's response
    response_text = message.content[0].text
    print("\n=== Claude says ===\n")
    print(response_text)
    print("\n=== Usage ===")
    print(f"Input tokens:  {message.usage.input_tokens}")
    print(f"Output tokens: {message.usage.output_tokens}")
    print(f"Model:         {message.model}\n")


if __name__ == "__main__":
    main()