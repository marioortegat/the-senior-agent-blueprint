# The Senior Agent Blueprint

Official code repository for the book **"The Senior Agent Blueprint: Production-Ready n8n Architectures"** by Mario Ortega.

## About this Repository

This repository contains the source code, n8n workflows (JSON), and Python scripts discussed in the book. Each folder corresponds to a specific chapter or architectural pattern.

## Repository Structure

| Chapter | Description | Status |
|---------|-------------|--------|
| [Chapter 03: MCP Server](./Chapter_03_MCP) | A production-ready Model Context Protocol server using SQLite and FastMCP | Available |
| [Chapter 04: DSPy Optimization](./Chapter_04_DSPy) | Prompt optimization with DSPy framework - Typed Predictors & Portable Prompts | Available |
| [Chapter 05: Memory Engine](./Chapter_05_Memory) | Modular vector memory system with ChromaDB | Available |
| [Chapter 06: Semantic Router](./Chapter_06_Semantic_Router) | Intelligent request routing and Semantic Firewall | Available |
| [Chapter 07: Agentic Patterns](./Chapter_07_Agentic_Patterns) | State Graph Engineering, Reflection, and Human-in-the-Loop | Available |
| [Chapter 08: Monitoring & Evals](./Chapter_08_Monitoring_Evals) | Tracing (Langfuse), Batch Scoring (RAGAS), PII Security (Presidio), and Intent Clustering | Available |

## Getting Started

1. **Clone this repository:**
   ```bash
   git clone https://github.com/marioortegat/the-senior-agent-blueprint.git
   cd the-senior-agent-blueprint
   ```

2. **Navigate to the chapter you are studying:**
   ```bash
   cd Chapter_03_MCP
   ```

3. **Follow the README.md inside each chapter folder** for specific setup instructions.

## Prerequisites

- Python 3.10+ (Tested extensively on Python 3.12)
- Node.js 18+ (for n8n)
- n8n (self-hosted or cloud)
- Basic understanding of AI agents and LLMs

## 🔧 Environment & Compatibility Notes

The AI engineering ecosystem (Langchain, Langfuse, RAGAS, etc.) evolves at a very rapid pace. To guarantee 100% stability and local execution compatibility across OS environments:
- **Strict Version Pinning:** The `requirements.txt` files inside each chapter contain strictly pinned versions. For example, Chapter 08 aligns `langfuse<3.0.0` with `langchain==0.2.x` and `ragas==0.1.19` to ensure smooth integration with lightweight Docker instances.
- **OS Compatibility:** Code has been patched and tested to run smoothly on Windows (e.g., forcing `utf-8` stdout encodings to prevent PowerShell emoji crashes) as well as macOS/Linux.

## Get the Book

Want to understand the architecture behind this code?

[Get The Senior Agent Blueprint](https://your-landing-page.com)

## Author

**Mario Ortega**
- GitHub: [@marioortegat](https://github.com/marioortegat)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

You are free to use this code in your personal and commercial projects.

## Contributing

Found a bug or want to improve the code? Pull requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'Add some improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request
