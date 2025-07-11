# Ready Tensor Agentic AI Certification – Week 6

Welcome to **Week 6** of the [Agentic AI Developer Certification Program](https://app.readytensor.ai/publications/HrJ0xWtLzLNt) by Ready Tensor!

[Last week](https://github.com/readytensor/rt-agentic-ai-cert-week5), you built your first **agentic systems** — intelligent assistants powered by LangGraph, memory, tools, and observability. This week, we take things further by shifting from **individual agents** to **multi-agent systems** that collaborate, specialize, and even debate.

---

## 🧠 What You'll Learn

Week 6 is all about **system architecture** — designing agentic systems composed of multiple, modular agents that interact meaningfully and reliably. You’ll go from developer to **agent system designer**.

By the end of the week, you’ll be able to:

- Design and implement multi-agent workflows
- Assign agent roles and manage collaboration boundaries
- Use LangGraph to orchestrate agent communication and shared memory
- Resolve tool conflicts and handle unreliable agent behavior
- Connect agents to external systems via **Model Context Protocol (MCP)**
- Architect resilient and modular systems ready for scale

---

## 📚 Lessons in This Repository

### Lesson 1 – [Building Blocks of Multi-Agent Systems](https://app.readytensor.ai/publications/architecting-intelligence-design-patterns-for-multi-agent-ai-systems-aaidc-week6-lesson-1-Sp2HOfRpH4Fl)

Understand the key components and patterns of agentic system design. Learn how agent teams are structured and what differentiates a multi-agent system from a single, complex agent.

### Lesson 2a – [Defining the Agentic Authoring Assistant](https://app.readytensor.ai/publications/from-idea-to-architecture-defining-our-agentic-authoring-assistant-aaidc-week6-lesson-2-Gq1xQ27DmJ56)

Introduce the Week 6 project: an Agentic Authoring Assistant. Define its overall goals and scope down to the tag extraction sub-project, setting the stage for implementation.

### Lesson 2b – [Building the Tag Extraction System](https://app.readytensor.ai/publications/from-architecture-to-implementation-building-the-tag-extraction-system-aaidc-week6-lesson-2b-D3vJsJh1500g)

Implement the tag extraction component using LangGraph. Combine traditional logic, ML models, and LLM reasoning — and explore when (and whether) agents are actually needed.

### Lesson 3a – [Designing Roles and Responsibilities](https://app.readytensor.ai/publications/building-the-dream-team-designing-the-right-agents-for-the-job-aaidc-week6-lesson-3a-qtRz3uuXGx5Y)

Explore how to define clear agent responsibilities and boundaries to reduce redundancy, improve clarity, and enable specialization in your systems.

### Lesson 3b – [Architectural Patterns for Multi-Agent Systems](https://app.readytensor.ai/publications/orchestrating-intelligence-designing-agentic-systems-that-actually-work-aaidc-week6-lesson-3b-redklSjefHNo)

Learn how to design agentic systems that produce coherent, coordinated outputs. Explore different architectural approaches — from simple sequential chains to sophisticated coordinated systems — and understand the trade-offs between complexity, quality, and efficiency.

### Lesson 4a – [Introduction to MCP](https://app.readytensor.ai/publications/mcp-a-standard-way-for-ai-to-use-external-tools-aaidc-week6-lecture-4a-LAeGUSWv4dKb)

Discover MCP (Model Context Protocol) — the universal standard that's doing for AI what HTTP did for the web. Learn how MCP solves integration chaos, provides built-in security, and enables AI agents to seamlessly connect with external tools and data sources through a standardized protocol.

### Lesson 4b – [MCP In Action](https://app.readytensor.ai/publications/mcp-in-action-connecting-and-creating-real-ai-integrations-aaidc-week6-lesson-4b-35v0wzEbKZBo)

Go from MCP theory to practice. Learn how to connect your AI to existing MCP servers (like GitHub, file systems, and databases) and build your own custom MCP server from scratch. Includes hands-on code walkthroughs and real-world integration examples.

---

## Repository Structure

```txt
rt-agentic-ai-cert-week6/
├── code/
│   ├── graphs/
│   │   ├── a3_graph.py                         # LangGraph definition for the A3 system
│   │   └── tag_generation_graph.py             # LangGraph definition for tag extraction flow
│   ├── nodes/
│   │   ├── a3_nodes.py                         # Nodes for the A3 system (manager, tldr, title, etc.)
│   │   ├── output_types.py                     # Pydantic output schemas for structured LLM responses
│   │   └── tag_generation.py                   # Nodes for tag extraction (LLM, spaCy, gazetteer, etc.)
│   ├── states/
│   │   ├── a3_state.py                         # LangGraph state class for the A3 system
│   │   └── tag_generation_state.py             # LangGraph state class for tag generation
│   ├── consts.py                               # Global constants for key names and node labels
│   ├── langgraph_utils.py                      # Utilities for visualizing LangGraphs and creating LLMs
│   ├── lesson2b_extract_entities.py            # Lesson 2b: Run entity/tag extraction pipeline
│   ├── lesson3b_a3_system.py                   # Lesson 3b: Run the full A3 authoring assistant system
│   ├── lesson4_mcp.py                          # Lesson 4: MCP integration demo
│   ├── llm.py                                  # LLM wrapper utility for structured outputs
│   ├── paths.py                                # Path management for input/output/config files
│   ├── prompt_builder.py                       # Utilities for building system and human prompts
│   └── utils.py                                # Shared helper functions
├── config/
│   ├── config.yaml                             # Main configuration file for agents and flows
│   ├── gazetteer_entities.yaml                 # Regex-based gazetteer entity definitions
│   └── reasoning.yaml                          # Example config for reasoning patterns (if used)
├── data/
│   ├── publication_example1.md                 # Sample input articles
│   ├── publication_example2.md
│   └── publication_example3.md
├── lessons/                                    # Lesson explanations and assets
├── outputs/                                    # Output files and visualizations (e.g., graph.png)
├── .env.example                                # Example environment file for API keys (e.g., Tavily)
├── .gitignore
├── LICENSE
├── README.md                                   # You are here
└── requirements.txt                            # Required Python dependencies

```

---

## Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/readytensor/rt-agentic-ai-cert-week6.git
   cd rt-agentic-ai-cert-week6
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment variables:**

   Copy the `.env.example` file and update it with your API keys and other required environment variables (e.g., for OpenAI or Tavily):

   ```bash
   cp .env.example .env
   ```

   - You can get your [Open AI API key](https://platform.openai.com/signup) for LLM access.
   - If using Tavily for search, sign up at [Tavily](https://www.tavily.com/) and add your API key to `.env`.

---

## Usage

This week's code supports three lessons with runnable scripts:

### 🏷️ Lesson 2b – Tag Extraction System

Run the tag extraction system on example articles:

```bash
python code/lesson2b_extract_entities.py
```

This script uses the tag extraction pipeline built in Lesson 2b and processes articles from the `data/` folder.

### 🧠 Lesson 3b – A3 (Agentic Authoring Assistant) System

Run the full A3 system that generates tags, TL;DR, title, and references:

```bash
python code/lesson3b_a3_system.py
```

This script integrates multiple agents developed across lessons into a cohesive multi-agent authoring system.

### 🔌 Lesson 4 – MCP Integration

Try out basic MCP integration for agent-to-tool communication:

```bash
python code/lesson4_mcp.py
```

This demo shows how to connect your agents to external systems using the **Model Context Protocol**, as taught in Lessons 4a and 4b.

You can modify or replace the input articles in the `data/` directory with your own content for experimentation.

---

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## Contact

**Ready Tensor, Inc.**

- Email: contact at readytensor dot com
- Issues & Contributions: Open an issue or pull request on this repository
- Website: [https://readytensor.ai](https://readytensor.ai)
