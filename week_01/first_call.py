"""Day 1 — first Claude API call, done the way the whole journey will be done:
streamed, measured, and logged to a database.

Run:
    uv add anthropic python-dotenv duckdb
    uv run first_call.py

Every concept here comes back in Project 1:
  - the client and a Messages API call
  - streaming tokens as they arrive
  - reading token usage off the response
  - logging usage + cost to DuckDB, then querying it with SQL
"""

import os
from datetime import datetime, timezone

import duckdb
from anthropic import Anthropic
from dotenv import load_dotenv

# --- setup -------------------------------------------------------------
load_dotenv()  # reads ANTHROPIC_API_KEY from .env (never hardcode keys)

if not os.environ.get("ANTHROPIC_API_KEY"):
    raise SystemExit("Missing ANTHROPIC_API_KEY — create a .env file first (see runbook Block 2).")

client = Anthropic()

# Check the current model list at platform.claude.com/docs — update as new models ship.
MODEL = "claude-sonnet-4-5"

# Rough public per-million-token prices; verify against current pricing page.
PRICE_IN_PER_MTOK = 3.00
PRICE_OUT_PER_MTOK = 15.00

DB_PATH = "journey.duckdb"

# --- database ----------------------------------------------------------
con = duckdb.connect(DB_PATH)
con.execute(
    """
    CREATE TABLE IF NOT EXISTS api_calls (
        called_at     TIMESTAMP,
        model         VARCHAR,
        prompt        VARCHAR,
        input_tokens  INTEGER,
        output_tokens INTEGER,
        est_cost_usd  DOUBLE
    )
    """
)

# --- the call ----------------------------------------------------------
prompt = (
    "In three sentences: I'm a BI developer starting a 25-week journey to become "
    "a Data + AI + Agentic AI engineer. Give me one piece of advice for week one."
)

print(f"\n>>> {prompt}\n")
print("--- Claude (streaming) ---")

with client.messages.stream(
    model=MODEL,
    max_tokens=300,
    messages=[{"role": "user", "content": prompt}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    response = stream.get_final_message()

print("\n--------------------------\n")

# --- measure and log ---------------------------------------------------
usage = response.usage
cost = (
    usage.input_tokens * PRICE_IN_PER_MTOK / 1_000_000
    + usage.output_tokens * PRICE_OUT_PER_MTOK / 1_000_000
)

con.execute(
    "INSERT INTO api_calls VALUES (?, ?, ?, ?, ?, ?)",
    [datetime.now(timezone.utc), MODEL, prompt, usage.input_tokens, usage.output_tokens, cost],
)

print(f"tokens in/out: {usage.input_tokens}/{usage.output_tokens}   est. cost: ${cost:.6f}")

# --- prove the data layer works: query your own usage with SQL ---------
print("\nAll calls so far (straight from DuckDB):")
print(
    con.execute(
        """
        SELECT called_at, input_tokens, output_tokens,
               ROUND(est_cost_usd, 6) AS cost_usd,
               ROUND(SUM(est_cost_usd) OVER (ORDER BY called_at), 6) AS running_cost  -- your first window function
        FROM api_calls
        ORDER BY called_at
        """
    ).fetchdf()
)

con.close()
print("\nDay 1 complete. Commit this. ✅")
