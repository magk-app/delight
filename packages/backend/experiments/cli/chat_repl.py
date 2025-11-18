"""Interactive Chat REPL with Real-Time Memory Visualization.

This is the main interface for chatting while seeing all memory operations:
- What memories are being queried
- What facts are being extracted
- What categories are being created
- What embeddings are generated
- Real-time search results

Run with:
    poetry run python experiments/cli/chat_repl.py
"""

import asyncio
import uuid
from datetime import datetime
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich import box

from experiments.database.json_storage import JSONStorage, JSONMemory
from experiments.memory.fact_extractor import FactExtractor
from experiments.memory.categorizer import DynamicCategorizer
from experiments.memory.embedding_service import EmbeddingService
from experiments.config import get_config


console = Console()


class ChatREPL:
    """Interactive chat with real-time memory visualization.

    Features:
    - See memories being created in real-time
    - See what facts are extracted from your messages
    - See search results as they're queried
    - See categorization happening live
    - Statistics and cost tracking
    """

    def __init__(self, user_id: Optional[uuid.UUID] = None):
        """Initialize chat REPL.

        Args:
            user_id: User ID (creates new if not provided)
        """
        self.console = console
        self.user_id = user_id or uuid.uuid4()

        # Initialize components
        self.console.print("\n[bold cyan]🔧 Initializing components...[/bold cyan]")
        self.storage = JSONStorage()
        self.fact_extractor = FactExtractor()
        self.categorizer = DynamicCategorizer()
        self.embedding_service = EmbeddingService()

        # Conversation history
        self.conversation: List[dict] = []

        # Statistics
        self.messages_sent = 0
        self.facts_created = 0
        self.searches_performed = 0

    def show_header(self):
        """Display header with instructions."""
        header = Panel(
            """[bold cyan]💬 Interactive Memory Chat[/bold cyan]

[yellow]Commands:[/yellow]
  📝 Type your message and press Enter to chat
  🔍 /search <query> - Search memories
  📊 /stats - Show statistics
  💾 /memories - List all your memories
  ❓ /help - Show this help
  👋 /exit - Exit chat

[green]What happens when you chat:[/green]
  1. Your message is analyzed for facts
  2. Facts are extracted and categorized
  3. Each fact becomes a separate memory
  4. Embeddings are generated for search
  5. You can see everything happening in real-time!
""",
            title="Welcome to Memory Chat",
            border_style="cyan",
            expand=False
        )
        self.console.print(header)
        self.console.print(f"\n[dim]User ID: {self.user_id}[/dim]")
        self.console.print(f"[dim]Storage: {self.storage.storage_path}[/dim]\n")

    async def process_message(self, message: str):
        """Process user message and show all memory operations.

        Args:
            message: User message
        """
        self.messages_sent += 1

        # Show what we're doing
        self.console.print("\n" + "=" * 70)
        self.console.print(f"[bold]You:[/bold] {message}")
        self.console.print("=" * 70)

        # Step 1: Extract facts
        self.console.print("\n[cyan]📝 Step 1: Extracting Facts...[/cyan]")
        extraction_result = await self.fact_extractor.extract_facts(message)

        if not extraction_result.facts:
            self.console.print("[yellow]⚠️  No facts extracted (message too simple)[/yellow]")
            return

        # Show extracted facts
        fact_table = Table(title="Extracted Facts", box=box.ROUNDED)
        fact_table.add_column("#", style="cyan", width=4)
        fact_table.add_column("Type", style="magenta", width=12)
        fact_table.add_column("Content", style="white")
        fact_table.add_column("Confidence", style="green", width=10)

        for i, fact in enumerate(extraction_result.facts, 1):
            fact_table.add_row(
                str(i),
                fact.fact_type.value.upper(),
                fact.content,
                f"{fact.confidence:.2f}"
            )

        self.console.print(fact_table)

        # Step 2: Categorize and create memories
        self.console.print("\n[cyan]🏷️  Step 2: Categorizing & Creating Memories...[/cyan]")

        memory_table = Table(title="Created Memories", box=box.ROUNDED)
        memory_table.add_column("#", style="cyan", width=4)
        memory_table.add_column("Content", style="white", width=40)
        memory_table.add_column("Categories", style="magenta")

        created_memories = []

        for i, fact in enumerate(extraction_result.facts, 1):
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

            created_memories.append(memory)
            self.facts_created += 1

            # Show in table
            categories_display = " → ".join(cat_result.categories[:3])
            if len(cat_result.categories) > 3:
                categories_display += "..."

            memory_table.add_row(
                str(i),
                fact.content[:40] + ("..." if len(fact.content) > 40 else ""),
                categories_display
            )

        self.console.print(memory_table)

        # Step 3: Show similar memories
        self.console.print("\n[cyan]🔍 Step 3: Finding Related Memories...[/cyan]")

        # Search for similar memories using the first fact
        if created_memories:
            first_memory = created_memories[0]
            query_embedding = first_memory.embedding

            similar_results = await self.storage.search_semantic(
                self.user_id,
                query_embedding,
                limit=3,
                threshold=0.6
            )

            if similar_results:
                similar_table = Table(title="Related Memories", box=box.ROUNDED)
                similar_table.add_column("Similarity", style="green", width=10)
                similar_table.add_column("Content", style="white")

                for memory, score in similar_results:
                    # Skip the memory we just created
                    if memory.id == first_memory.id:
                        continue

                    similar_table.add_row(
                        f"{score:.3f}",
                        memory.content[:60] + ("..." if len(memory.content) > 60 else "")
                    )

                self.console.print(similar_table)
            else:
                self.console.print("[dim]No similar memories found[/dim]")

        # Summary
        self.console.print(f"\n[bold green]✅ Created {len(created_memories)} new memories![/bold green]")

    async def search_memories(self, query: str):
        """Search memories and show results.

        Args:
            query: Search query
        """
        self.searches_performed += 1

        self.console.print(f"\n[cyan]🔍 Searching for: \"{query}\"[/cyan]\n")

        # Generate query embedding
        query_embedding = await self.embedding_service.embed_text(query)

        # Semantic search
        semantic_results = await self.storage.search_semantic(
            self.user_id,
            query_embedding,
            limit=5,
            threshold=0.5
        )

        if semantic_results:
            results_table = Table(title="Search Results (Semantic)", box=box.ROUNDED)
            results_table.add_column("Score", style="green", width=8)
            results_table.add_column("Content", style="white", width=50)
            results_table.add_column("Categories", style="magenta")

            for memory, score in semantic_results:
                categories = memory.metadata.get("categories", [])
                categories_display = ", ".join(categories[:2])
                if len(categories) > 2:
                    categories_display += "..."

                results_table.add_row(
                    f"{score:.3f}",
                    memory.content,
                    categories_display
                )

            self.console.print(results_table)
        else:
            self.console.print("[yellow]No results found[/yellow]")

    def show_all_memories(self):
        """Show all user memories."""
        stats = self.storage.get_statistics()

        self.console.print(f"\n[cyan]💾 Your Memories[/cyan]")
        self.console.print(f"Total: {stats['total_memories']} memories\n")

        # Get recent memories
        memories = list(self.storage.memories.values())
        user_memories = [m for m in memories if m.user_id == self.user_id]
        user_memories.sort(key=lambda m: m.created_at, reverse=True)

        if user_memories:
            memory_table = Table(title="Recent Memories (Last 10)", box=box.ROUNDED)
            memory_table.add_column("Time", style="dim", width=12)
            memory_table.add_column("Content", style="white", width=50)
            memory_table.add_column("Type", style="magenta", width=12)

            for memory in user_memories[:10]:
                time_str = memory.created_at.strftime("%H:%M:%S")
                fact_type = memory.metadata.get("fact_type", "unknown")

                memory_table.add_row(
                    time_str,
                    memory.content,
                    fact_type.upper()
                )

            self.console.print(memory_table)
        else:
            self.console.print("[dim]No memories yet. Start chatting to create some![/dim]")

    def show_statistics(self):
        """Show usage statistics."""
        stats_panel = Panel(
            f"""[bold cyan]📊 Session Statistics[/bold cyan]

[yellow]Activity:[/yellow]
  Messages Sent:      {self.messages_sent}
  Facts Created:      {self.facts_created}
  Searches Performed: {self.searches_performed}

[yellow]Storage:[/yellow]
  Total Memories:     {len(self.storage.memories)}
  Your Memories:      {len([m for m in self.storage.memories.values() if m.user_id == self.user_id])}

[yellow]API Usage:[/yellow]
  Embedding Requests: {self.embedding_service.total_requests}
  Total Tokens:       {self.embedding_service.total_tokens:,}
  Cost (USD):         ${self.embedding_service.total_cost_usd:.4f}

[yellow]Fact Extraction:[/yellow]
  Extractions:        {self.fact_extractor.total_extractions}
  Facts Extracted:    {self.fact_extractor.total_facts_extracted}
  Tokens Used:        {self.fact_extractor.total_tokens_used:,}
""",
            title="Statistics",
            border_style="cyan"
        )

        self.console.print(stats_panel)

    async def run(self):
        """Run the interactive chat REPL."""
        self.show_header()

        while True:
            try:
                # Get user input
                user_input = self.console.input("\n[bold cyan]You:[/bold cyan] ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    command = user_input[1:].lower()

                    if command == "exit" or command == "quit":
                        self.console.print("\n[bold]👋 Goodbye![/bold]\n")
                        break

                    elif command == "help":
                        self.show_header()

                    elif command == "stats":
                        self.show_statistics()

                    elif command == "memories":
                        self.show_all_memories()

                    elif command.startswith("search "):
                        query = command[7:].strip()
                        if query:
                            await self.search_memories(query)
                        else:
                            self.console.print("[yellow]Usage: /search <query>[/yellow]")

                    else:
                        self.console.print(f"[yellow]Unknown command: {command}[/yellow]")
                        self.console.print("[dim]Type /help for available commands[/dim]")

                else:
                    # Process as chat message
                    await self.process_message(user_input)

            except KeyboardInterrupt:
                self.console.print("\n\n[bold]👋 Goodbye![/bold]\n")
                break

            except Exception as e:
                self.console.print(f"\n[red]❌ Error: {e}[/red]")
                import traceback
                traceback.print_exc()


async def main():
    """Main entry point."""
    repl = ChatREPL()
    await repl.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\n[bold]👋 Goodbye![/bold]\n")
