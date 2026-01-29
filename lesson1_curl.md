# Lesson 1: OpenAI Responses API with cURL

## Basic Request (without tools)

```bash
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5.2",
    "input": "Tell me where Crazy Town in Tampere is located."
  }'
```

### Response

```json
{
  "id": "resp_0aa21d50be82c5c400695fc28db9ec81958d1253b6dab05c66",
  "object": "response",
  "created_at": 1767883405,
  "status": "completed",
  "background": false,
  "billing": {
    "payer": "developer"
  },
  "completed_at": 1767883407,
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "max_tool_calls": null,
  "model": "gpt-5.2-2025-12-11",
  "output": [
    {
      "id": "msg_0aa21d50be82c5c400695fc28e3a28819594b3814068fae9ab",
      "type": "message",
      "status": "completed",
      "content": [
        {
          "type": "output_text",
          "annotations": [],
          "logprobs": [],
          "text": "Crazy Town (the co-working/community hub) in Tampere is located at:\n\n**Näsilinnankatu 22 A, 33210 Tampere, Finland** (near the city centre / Hämeenkatu area)."
        }
      ],
      "role": "assistant"
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "prompt_cache_key": null,
  "prompt_cache_retention": null,
  "reasoning": {
    "effort": "none",
    "summary": null
  },
  "safety_identifier": null,
  "service_tier": "default",
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    },
    "verbosity": "medium"
  },
  "tool_choice": "auto",
  "tools": [],
  "top_logprobs": 0,
  "top_p": 0.98,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 17,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 51,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 68
  },
  "user": null,
  "metadata": {}
}
```

## With Web Search Tool Enabled

```bash
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5.2",
    "tools": [
        { "type": "web_search" }
    ],
    "input": "Tell me where Crazy Town in Tampere is located."
  }'
```

### Response

```json
{
  "id": "resp_01a9e255562350cd00695fcb81824881a39ce40365ff1e7d81",
  "object": "response",
  "created_at": 1767885697,
  "status": "completed",
  "background": false,
  "billing": {
    "payer": "developer"
  },
  "completed_at": 1767885701,
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "max_tool_calls": null,
  "model": "gpt-5.2-2025-12-11",
  "output": [
    {
      "id": "ws_01a9e255562350cd00695fcb822b3081a3af9e79478a96d81a",
      "type": "web_search_call",
      "status": "completed",
      "action": {
        "type": "search",
        "queries": [
          "Crazy Town Tampere location address",
          "Crazy Town Tampere Crazy Town Oy address Tampere"
        ],
        "query": "Crazy Town Tampere location address"
      }
    },
    {
      "id": "msg_01a9e255562350cd00695fcb83600481a39ea770406484b868",
      "type": "message",
      "status": "completed",
      "content": [
        {
          "type": "output_text",
          "annotations": [
            {
              "type": "url_citation",
              "end_index": 218,
              "start_index": 139,
              "title": "Modern Offices Tampere | Come and see!",
              "url": "https://crazytown.fi/en/toimitilat/tampere/?utm_source=openai"
            },
            {
              "type": "url_citation",
              "end_index": 449,
              "start_index": 374,
              "title": "Tampere – https://crazytown.fi/",
              "url": "https://crazytown.fi/sijainnit/tampere/?utm_source=openai"
            }
          ],
          "logprobs": [],
          "text": "Crazy Town Tampere is located at:\n\n**Pakkahuoneenaukio 2, 33100 Tampere, Finland** (Crazy Town "Pendoliino", next to the railway station). ([crazytown.fi](https://crazytown.fi/en/toimitilat/tampere/?utm_source=openai))\n\n(Older sources mention the previous address **Rautatienkatu 21** in Tampere, but Crazy Town's current Tampere location is listed as Pakkahuoneenaukio 2.) ([crazytown.fi](https://crazytown.fi/sijainnit/tampere/?utm_source=openai))"
        }
      ],
      "role": "assistant"
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "prompt_cache_key": null,
  "prompt_cache_retention": null,
  "reasoning": {
    "effort": "none",
    "summary": null
  },
  "safety_identifier": null,
  "service_tier": "default",
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    },
    "verbosity": "medium"
  },
  "tool_choice": "auto",
  "tools": [
    {
      "type": "web_search",
      "filters": null,
      "search_context_size": "medium",
      "user_location": {
        "type": "approximate",
        "city": null,
        "country": "US",
        "region": null,
        "timezone": null
      }
    }
  ],
  "top_logprobs": 0,
  "top_p": 0.98,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 8483,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 182,
    "output_tokens_details": {
      "reasoning_tokens": 52
    },
    "total_tokens": 8665
  },
  "user": null,
  "metadata": {}
}
```
