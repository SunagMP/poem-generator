# 🎭 PoemCraft: An LLM-Powered Poem Generation & Optimization Workflow

This repository contains an LLM-powered poem generator built using [LangChain](https://www.langchain.com/) and [LangGraph](https://www.langgraph.dev/). It generates emotionally rich poems based on a given scenario, evaluates them, and optimizes iteratively based on structured feedback.

---

## ✨ Features

- 🎨 **Poem Generator Node** – Uses a custom prompt to create a 15–20 line poem with emotions explicitly mentioned in brackets `(like this)`.
- 🧠 **Evaluator Node** – Evaluates the poem on emotional depth, word simplicity, and rhyming, giving a score and improvement feedback.
- 🔁 **Optimizer Node** – Refines the poem based on evaluator feedback while retaining the original tone/emotion.
- 🔄 **Iterative Workflow** – Loops through evaluate → optimize → evaluate until a satisfactory score is reached.

---

## 🚀 Setup Instructions
1. 📦 Clone the Repository
- git clone https://github.com/your-username/langgraph-poem-generator.git
- cd langgraph-poem-generator
2. 🐍 Create a Virtual Environment
- python -m venv myenv
- source myenv/bin/activate          # On Linux/macOS
- myenv\Scripts\activate             # On Windows
3. 📥 Install Dependencies
- pip install -r requirements.txt
4. 🔑 Set Environment Variables
- You'll need an API key for Google Gemini.
- GOOGLE_API_KEY=your_api_key_here
5. Run the below command
  python main.py

## 🛠️ Architecture

```mermaid
graph TD;
    Start --> Generator
    Generator --> Evaluator
    Evaluator -->|score >= threshold| End
    Evaluator -->|score < threshold| Optimizer
    Optimizer --> Evaluator
