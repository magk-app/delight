"""Conversational AI Chatbot with Memory Integration.

This chatbot:
- Retrieves relevant memories when you ask questions
- Uses memories to provide personalized responses
- Creates new memories from your messages
- Shows what memories it's using in real-time

Run with:
    poetry run python experiments/cli/chatbot.py
"""

import asyncio
import uuid
from datetime import datetime
from typing import List, Optional

from openai import AsyncOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from experiments.database.json_storage import JSONStorage
from experiments.memory.fact_extractor import FactExtractor
from experiments.memory.categorizer import DynamicCategorizer
from experiments.memory.embedding_service import EmbeddingService
from experiments.config import get_config


console = Console()


class MemoryChatbot:
    """Conversational AI that uses memories to respond.

    This chatbot:
    1. Searches your memories for relevant context
    2. Uses that context to provide personalized responses
    3. Extracts facts from your messages
    4. Creates new memories
    5. Shows everything happening in real-time
    """

    def __init__(self, user_id: Optional[uuid.UUID] = None):
        """Initialize chatbot.

        Args:
            user_id: User ID (creates new if not provided)
        """
        self.console = console
        self.user_id = user_id or uuid.uuid4()
        self.config = get_config()

        # Initialize components
        self.console.print("\n[bold cyan]🔧 Initializing AI chatbot...[/bold cyan]")
        self.storage = JSONStorage()
        self.fact_extractor = FactExtractor()
        self.categorizer = DynamicCategorizer()
        self.embedding_service = EmbeddingService()
        self.openai = AsyncOpenAI(api_key=self.config.openai_api_key)

        # Conversation history for context
        self.conversation_history = []

        # Statistics
        self.messages_exchanged = 0
        self.memories_created = 0
        self.memories_retrieved = 0

    def show_header(self):
        """Display welcome header."""
        header = Panel(
            """[bold cyan]🤖 AI Chatbot with Memory[/bold cyan]

[yellow]I'm an AI assistant with access to your personal memories.[/yellow]

[green]What I can do:[/green]
  💬 Have natural conversations with you
  🧠 Remember facts about you
  🔍 Search my memories to answer your questions
  📝 Create new memories from our conversation
  📊 Show you which memories I'm using

[yellow]Commands:[/yellow]
  💬 Just chat naturally!
  🔍 /search <query> - Search memories
  💾 /memories - View all memories
  📊 /stats - Show statistics
  🗑️  /clear - Clear conversation history
  ❓ /help - Show this help
  👋 /exit - Exit

[dim]I'll show you which memories I retrieve and create in real-time![/dim]
""",
            title="Welcome to Memory Chatbot",
            border_style="cyan",
            expand=False
        )
        self.console.print(header)
        self.console.print(f"\n[dim]User ID: {self.user_id}[/dim]")
        self.console.print(f"[dim]Clean memories: {self.storage.storage_path.parent / 'memories_clean.json'}[/dim]\n")

    async def retrieve_relevant_memories(self, message: str, limit: int = 5) -> List:
        """Retrieve memories relevant to the message.

        Args:
            message: User message
            limit: Maximum memories to retrieve

        Returns:
            List of (memory, score) tuples
        """
        # Generate embedding for message
        message_embedding = await self.embedding_service.embed_text(message)

        # Search for relevant memories
        results = await self.storage.search_semantic(
            self.user_id,
            message_embedding,
            limit=limit,
            threshold=0.5  # Lower threshold to get more context
        )

        self.memories_retrieved += len(results)
        return results

    async def generate_response(
        self,
        message: str,
        relevant_memories: List
    ) -> str:
        """Generate AI response using retrieved memories.

        Args:
            message: User message
            relevant_memories: List of (memory, score) tuples

        Returns:
            AI response
        """
        # Build context from memories
        memory_context = ""
        if relevant_memories:
            memory_context = "\n\nRelevant memories about the user:\n"
            for memory, score in relevant_memories:
                memory_context += f"- {memory.content}\n"

        # Build system prompt
        system_prompt = f"""You are a helpful AI assistant with access to the user's personal memories.

Use the provided memories to give personalized, contextual responses.
Be conversational and natural.
Reference specific memories when relevant.
{memory_context}"""

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Generate response
        response = await self.openai.chat.completions.create(
            model=self.config.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                *self.conversation_history[-10:]  # Last 10 messages for context
            ],
            temperature=0.7,
            max_tokens=500
        )

        assistant_message = response.choices[0].message.content

        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    async def create_memories_from_message(self, message: str):
        """Extract facts and create memories from message.

        Args:
            message: User message
        """
        # Extract facts
        extraction_result = await self.fact_extractor.extract_facts(message)

        if not extraction_result.facts:
            return []

        created_memories = []

        for fact in extraction_result.facts:
            # Categorize
            cat_result = await self.categorizer.categorize(fact.content)

            # Generate embedding
            embedding = await self.embedding_service.embed_text(fact.content)

            # Create memory
            memory = await self.storage.create_memory(
                user_id=self.user_id,
                content=fact.content,
                memory_type="personal",
                embedding=embedding,
                metadata={
                    "fact_type": fact.fact_type.value,
                    "confidence": fact.confidence,
                    "categories": cat_result.categories,
                    "category_hierarchy": (
                        cat_result.hierarchy.to_path()
                        if cat_result.hierarchy
                        else None
                    ),
                    "source_message": message,
                    "created_at": datetime.now().isoformat()
                }
            )

            created_memories.append((fact, memory))
            self.memories_created += 1

        return created_memories

    async def chat(self, message: str):
        """Process message and respond.

        Args:
            message: User message
        """
        self.messages_exchanged += 1

        self.console.print("\n" + "─" * 70)
        self.console.print(f"[bold cyan]You:[/bold cyan] {message}")
        self.console.print("─" * 70)

        # Step 1: Retrieve relevant memories
        self.console.print("\n[dim]🔍 Searching memories...[/dim]")
        relevant_memories = await self.retrieve_relevant_memories(message)

        if relevant_memories:
            # Show retrieved memories
            memory_table = Table(
                title="🧠 Retrieved Memories (Used for Response)",
                box=box.SIMPLE,
                show_header=True,
                header_style="bold magenta"
            )
            memory_table.add_column("Score", style="green", width=6)
            memory_table.add_column("Memory", style="white")

            for memory, score in relevant_memories:
                memory_table.add_row(
                    f"{score:.2f}",
                    memory.content[:70] + ("..." if len(memory.content) > 70 else "")
                )

            self.console.print(memory_table)
        else:
            self.console.print("[dim]No relevant memories found[/dim]")

        # Step 2: Generate AI response
        self.console.print("\n[dim]💭 Generating response...[/dim]")
        response = await self.generate_response(message, relevant_memories)

        # Show response
        response_panel = Panel(
            response,
            title="🤖 Assistant",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(response_panel)

        # Step 3: Extract facts and create memories
        self.console.print("\n[dim]📝 Extracting facts from your message...[/dim]")
        created_memories = await self.create_memories_from_message(message)

        if created_memories:
            # Show created memories
            creation_table = Table(
                title="✨ New Memories Created",
                box=box.SIMPLE,
                show_header=True,
                header_style="bold cyan"
            )
            creation_table.add_column("Fact", style="white", width=50)
            creation_table.add_column("Categories", style="magenta")

            for fact, memory in created_memories:
                categories = memory.metadata.get("categories", [])
                categories_display = " → ".join(categories[:3])

                creation_table.add_row(
                    fact.content,
                    categories_display
                )

            self.console.print(creation_table)
            self.console.print(f"\n[green]✓ Created {len(created_memories)} new memories[/green]")
        else:
            self.console.print("[dim]No new facts to memorize[/dim]")

    async def search_memories(self, query: str):
        """Search and display memories.

        Args:
            query: Search query
        """
        self.console.print(f"\n[cyan]🔍 Searching: \"{query}\"[/cyan]\n")

        query_embedding = await self.embedding_service.embed_text(query)
        results = await self.storage.search_semantic(
            self.user_id,
            query_embedding,
            limit=10,
            threshold=0.4
        )

        if results:
            results_table = Table(title="Search Results", box=box.ROUNDED)
            results_table.add_column("Score", style="green", width=8)
            results_table.add_column("Content", style="white")
            results_table.add_column("Type", style="magenta", width=12)

            for memory, score in results:
                fact_type = memory.metadata.get("fact_type", "unknown")
                results_table.add_row(
                    f"{score:.3f}",
                    memory.content,
                    fact_type.upper()
                )

            self.console.print(results_table)
        else:
            self.console.print("[yellow]No results found[/yellow]")

    def show_memories(self):
        """Show all user memories."""
        memories = list(self.storage.memories.values())
        user_memories = [m for m in memories if m.user_id == self.user_id]
        user_memories.sort(key=lambda m: m.created_at, reverse=True)

        if not user_memories:
            self.console.print("\n[dim]No memories yet[/dim]")
            return

        self.console.print(f"\n[cyan]💾 Your Memories ({len(user_memories)} total)[/cyan]\n")

        memory_table = Table(title="All Memories", box=box.ROUNDED)
        memory_table.add_column("Time", style="dim", width=19)
        memory_table.add_column("Content", style="white", width=45)
        memory_table.add_column("Type", style="magenta", width=12)

        for memory in user_memories[:20]:  # Show last 20
            time_str = memory.created_at.strftime("%Y-%m-%d %H:%M:%S")
            fact_type = memory.metadata.get("fact_type", "unknown")

            memory_table.add_row(
                time_str,
                memory.content,
                fact_type.upper()
            )

        self.console.print(memory_table)

        if len(user_memories) > 20:
            self.console.print(f"\n[dim]... and {len(user_memories) - 20} more[/dim]")

        # Show clean file location
        clean_path = self.storage.storage_path.parent / "memories_clean.json"
        self.console.print(f"\n[dim]💡 View clean version: {clean_path}[/dim]")

    def show_statistics(self):
        """Show usage statistics."""
        stats_panel = Panel(
            f"""[bold cyan]📊 Session Statistics[/bold cyan]

[yellow]Conversation:[/yellow]
  Messages Exchanged:  {self.messages_exchanged}
  Memories Created:    {self.memories_created}
  Memories Retrieved:  {self.memories_retrieved}

[yellow]Storage:[/yellow]
  Total Memories:      {len(self.storage.memories)}
  Your Memories:       {len([m for m in self.storage.memories.values() if m.user_id == self.user_id])}

[yellow]API Usage:[/yellow]
  Embedding Requests:  {self.embedding_service.total_requests}
  Total Tokens:        {self.embedding_service.total_tokens:,}
  Cost (USD):          ${self.embedding_service.total_cost_usd:.4f}

[yellow]Files:[/yellow]
  Full: {self.storage.storage_path.name}
  Clean: memories_clean.json (no embeddings)
""",
            title="Statistics",
            border_style="cyan"
        )

        self.console.print(stats_panel)

    async def run(self):
        """Run the conversational chatbot."""
        self.show_header()

        self.console.print("[bold green]🎉 Ready to chat! Ask me anything or tell me about yourself.[/bold green]\n")

        while True:
            try:
                # Get user input
                user_input = self.console.input("\n[bold cyan]You:[/bold cyan] ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    command = user_input[1:].lower()

                    if command in ["exit", "quit"]:
                        self.console.print("\n[bold]👋 Goodbye! Your memories are saved.[/bold]\n")
                        break

                    elif command == "help":
                        self.show_header()

                    elif command == "stats":
                        self.show_statistics()

                    elif command == "memories":
                        self.show_memories()

                    elif command == "clear":
                        self.conversation_history = []
                        self.console.print("\n[green]✓ Conversation history cleared[/green]")

                    elif command.startswith("search "):
                        query = command[7:].strip()
                        if query:
                            await self.search_memories(query)
                        else:
                            self.console.print("[yellow]Usage: /search <query>[/yellow]")

                    else:
                        self.console.print(f"[yellow]Unknown command: {command}[/yellow]")
                        self.console.print("[dim]Type /help for commands[/dim]")

                else:
                    # Chat!
                    await self.chat(user_input)

            except KeyboardInterrupt:
                self.console.print("\n\n[bold]👋 Goodbye![/bold]\n")
                break

            except Exception as e:
                self.console.print(f"\n[red]❌ Error: {e}[/red]")
                import traceback
                traceback.print_exc()


async def main():
    """Main entry point."""
    chatbot = MemoryChatbot()
    await chatbot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\n[bold]👋 Goodbye![/bold]\n")
