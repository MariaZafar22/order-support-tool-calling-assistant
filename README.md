# 🤖 Order Support Tool-Calling Assistant

An AI assistant that doesn't just talk — it **takes action**. Built with **Gemini function calling**, it decides when to look up an order, asks the application to run a tool, and turns the result into a clear, natural-language answer.

## 🔍 **What It Does**
A customer asks something like *"Where is my order ORD-101?"*. The AI recognizes that it needs live data, requests the `check_order_status` tool with the right argument, and replies using only the information the tool returns. Questions that need no tool (like general knowledge) are answered directly.

## ⚙️ **How It Works**
1. The tool is described to the model (name, purpose, parameters).
2. The user sends a natural-language request.
3. The model decides whether a tool is needed and returns the **tool name and arguments**.
4. **The application executes the function**, not the model.
5. The result is sent back and the model writes the **final response**.

`User request → LLM → tool request → application runs function → result → LLM → final answer`

## 🛡️ **Safety Design**
- The model can only request tools from an **allow-list** (`AVAILABLE_TOOLS`); it never runs arbitrary code.
- The system prompt forces answers to rely **only on tool results**.
- Unknown order IDs return `found: False`, so the assistant reports the problem instead of inventing details.

## 🧪 **Test Cases**
| # | Request | Expected behavior |
|---|---------|-------------------|
| 1 | "Where is my order ORD-101?" | Calls the tool, reports shipped status |
| 2 | "Has ORD-103 been delivered yet?" | Calls the tool, different wording |
| 3 | "What is the capital of France?" | Answers directly, **no tool call** |
| 4 | "Can you check the status of order ORD-999?" | Tool finds nothing, AI says order not found |

Each run prints three clear stages: **[1] AI TOOL REQUEST**, **[2] APP EXECUTED**, **[3] FINAL RESPONSE**.

## 🚀 **Getting Started**
```bash
pip install -r requirements.txt
python tool_calling_assistant.py
```
You will be asked for a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey). The key is entered at runtime and **never stored in the code**.

## 📁 **Project Structure**
```
order-support-tool-calling-assistant/
├── tool_calling_assistant.py   # tool, tool definition and calling loop
├── requirements.txt            # dependencies
├── .gitignore
└── README.md
```

## 🧰 **Tech Stack**
Python · Google Gemini API (`google-genai`) · Function / Tool Calling

## 🔮 **Possible Improvements**
- Add more tools (cancel order, product price, create support ticket)
- Connect to a real database or API
- Add conversation memory for multi-turn chats
