"""Conversational AI Chatbot with PostgreSQL Memory Integration.

This chatbot:
- Retrieves relevant memories from PostgreSQL when you chat
- Uses memories to provide personalized responses via OpenAI
- Creates new memories from your messages
- Shows what memories it's using in real-time
- Stores everything in the database with pgvector semantic search

Run with:
    poetry run python experiments/cli/chatbot.py
"""

import asyncio
import uuid
from typing import List, Optional
from uuid import UUID

from openai import AsyncOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from app.db.session import AsyncSessionLocal
from app.models.memory import MemoryType
from experiments.config import get_config
from experiments.memory.memory_service import MemoryService
from experiments.memory.types import SearchResult


console = Console()


class MemoryChatbot:
    """Conversational AI that uses PostgreSQL memories to respond.

    This chatbot:
    1. Searches PostgreSQL for relevant memories using semantic search
    2. Uses that context to provide personalized responses via GPT-4o-mini
    3. Extracts facts from your messages using LLM
    4. Creates new memories in PostgreSQL with embeddings
    5. Shows everything happening in real-time
    """

    def __init__(self, user_id: Optional[UUID] = None):
        """Initialize chatbot.

        Args:
            user_id: User ID (creates new if not provided)
        """
        self.console = console
        self.user_id = user_id or uuid.uuid4()
        self.config = get_config()

        # Initialize components
        self.console.print("\n[bold cyan]🔧 Initializing AI chatbot with PostgreSQL...[/bold cyan]")
        self.memory_service = MemoryService()
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
            """[bold cyan]🤖 AI Chatbot with PostgreSQL Memory[/bold cyan]

[yellow]I'm an AI assistant with access to your personal memories stored in PostgreSQL.[/yellow]

[green]What I can do:[/green]
  💬 Have natural conversations with you
  🧠 Remember facts about you (stored in PostgreSQL)
  🔍 Search my memories using semantic search (pgvector)
  📝 Create new memories from our conversation
  📊 Show you which memories I'm using

[yellow]Commands:[/yellow]
  💬 Just chat naturally!
  🔍 /search <query> - Search memories semantically
  💾 /memories - View all your memories
  📊 /stats - Show statistics
  🗑️  /clear - Clear conversation history
  ❓ /help - Show this help
  👋 /exit - Exit

[dim]I'll show you which memories I retrieve and create in real-time![/dim]
[dim]All memories are stored in PostgreSQL with vector embeddings for semantic search.[/dim]
""",
            title="Welcome to Memory Chatbot",
            border_style="cyan",
            expand=False
        )
        self.console.print(header)
        self.console.print(f"\n[dim]User ID: {self.user_id}[/dim]")
        self.console.print(f"[dim]Database: PostgreSQL with pgvector[/dim]\n")

    async def retrieve_relevant_memories(self, message: str, limit: int = 5) -> List[SearchResult]:
        """Retrieve memories relevant to the message from PostgreSQL.

        Args:
            message: User message
            limit: Maximum memories to retrieve

        Returns:
            List of SearchResult objects
        """
        async with AsyncSessionLocal() as db:
            try:
                # Search using memory service with auto-routing
                results = await self.memory_service.search_memories(
                    user_id=self.user_id,
                    query=message,
                    db=db,
                    auto_route=True,  # Automatically selects best search strategy
                    limit=limit,
                    memory_types=[MemoryType.PERSONAL, MemoryType.PROJECT]  # Include personal and project memories
                )
                self.memories_retrieved += len(results)
                await db.commit()
                return results
            except Exception:
                await db.rollback()
                raise

    async def generate_response(
        self,
        message: str,
        relevant_memories: List[SearchResult]
    ) -> str:
        """Generate AI response using retrieved memories.

        Args:
            message: User message
            relevant_memories: List of SearchResult objects

        Returns:
            AI response
        """
        # Build context from memories
        memory_context = ""
        if relevant_memories:
            memory_context = "\n\nRelevant memories about the user:\n"
            for result in relevant_memories:
                memory_context += f"- {result.content} (relevance: {result.score:.2f})\n"

        # Build system prompt
        system_prompt = f"""You are a helpful AI assistant with access to the user's personal memories stored in PostgreSQL.

Use the provided memories to give personalized, contextual responses.
Be conversational and natural.
Reference specific memories when relevant.
If no memories are provided, respond naturally without making assumptions.
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

    async def create_memories_from_message(self, message: str) -> List:
        """Extract facts and create memories from message in PostgreSQL.

        Args:
            message: User message

        Returns:
            List of created Memory objects
        """
        async with AsyncSessionLocal() as db:
            try:
                # Use memory service to create memories with fact extraction
                memories = await self.memory_service.create_memory_from_message(
                    user_id=self.user_id,
                    message=message,
                    memory_type=MemoryType.PERSONAL,
                    db=db,
                    extract_facts=True,  # Extract discrete facts
                    auto_categorize=True,  # Auto-categorize each fact
                    generate_embeddings=True,  # Generate embeddings for search
                    link_facts=True  # Link related facts in graph
                )
                self.memories_created += len(memories)
                await db.commit()
                return memories
            except Exception:
                await db.rollback()
                raise

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
            memory_table.add_column("Type", style="cyan", width=10)
            memory_table.add_column("Memory", style="white")

            for result in relevant_memories:
                memory_table.add_row(
                    f"{result.score:.2f}",
                    result.memory_type.upper(),
                    result.content[:60] + ("..." if len(result.content) > 60 else "")
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
            creation_table.add_column("Content", style="white", width=50)
            creation_table.add_column("Categories", style="magenta")

            for memory in created_memories:
                categories = memory.extra_data.get("categories", []) if memory.extra_data else []
                categories_display = " → ".join(categories[:3]) if categories else "uncategorized"

                creation_table.add_row(
                    memory.content[:50] + ("..." if len(memory.content) > 50 else ""),
                    categories_display
                )

            self.console.print(creation_table)
            self.console.print(f"\n[green]✓ Created {len(created_memories)} new memories in PostgreSQL[/green]")
        else:
            self.console.print("[dim]No new facts to memorize[/dim]")

    async def search_memories(self, query: str):
        """Search and display memories from PostgreSQL.

        Args:
            query: Search query
        """
        self.console.print(f"\n[cyan]🔍 Searching: \"{query}\"[/cyan]\n")

        async with AsyncSessionLocal() as db:
            try:
                results = await self.memory_service.search_memories(
                    user_id=self.user_id,
                    query=query,
                    db=db,
                    auto_route=True,
                    limit=10,
                    memory_types=[MemoryType.PERSONAL, MemoryType.PROJECT]
                )

                if results:
                    results_table = Table(title="Search Results", box=box.ROUNDED)
                    results_table.add_column("Score", style="green", width=8)
                    results_table.add_column("Type", style="cyan", width=10)
                    results_table.add_column("Content", style="white")

                    for result in results:
                        results_table.add_row(
                            f"{result.score:.3f}",
                            result.memory_type.upper(),
                            result.content
                        )

                    self.console.print(results_table)
                else:
                    self.console.print("[yellow]No results found[/yellow]")
                await db.commit()
            except Exception:
                await db.rollback()
                raise

    async def show_memories(self):
        """Show all user memories from PostgreSQL."""
        async with AsyncSessionLocal() as db:
            try:
                # Search for all memories (broad query)
                results = await self.memory_service.search_memories(
                    user_id=self.user_id,
                    query="all memories",  # Use a broad query instead of empty
                    db=db,
                    auto_route=True,
                    limit=50,
                    memory_types=[MemoryType.PERSONAL, MemoryType.PROJECT, MemoryType.TASK]
                )

                if not results:
                    self.console.print("\n[dim]No memories yet. Start chatting to create some![/dim]")
                    return

                self.console.print(f"\n[cyan]💾 Your Memories ({len(results)} shown)[/cyan]\n")

                memory_table = Table(title="Recent Memories", box=box.ROUNDED)
                memory_table.add_column("Type", style="cyan", width=10)
                memory_table.add_column("Content", style="white", width=50)
                memory_table.add_column("Score", style="green", width=8)

                for result in results[:20]:  # Show last 20
                    memory_table.add_row(
                        result.memory_type.upper(),
                        result.content[:50] + ("..." if len(result.content) > 50 else ""),
                        f"{result.score:.2f}" if result.score else "N/A"
                    )

                self.console.print(memory_table)

                if len(results) > 20:
                    self.console.print(f"\n[dim]... and {len(results) - 20} more[/dim]")
                await db.commit()
            except Exception:
                await db.rollback()
                raise

    def show_statistics(self):
        """Show usage statistics."""
        service_stats = self.memory_service.get_statistics()
        embedding_stats = service_stats.get("embedding_service", {})
        
        stats_panel = Panel(
            f"""[bold cyan]📊 Session Statistics[/bold cyan]

[yellow]Conversation:[/yellow]
  Messages Exchanged:  {self.messages_exchanged}
  Memories Created:    {self.memories_created}
  Memories Retrieved:  {self.memories_retrieved}

[yellow]Memory Service:[/yellow]
  Total Memories Created:  {service_stats.get('total_memories_created', 0)}
  Facts Extracted:         {service_stats.get('total_facts_extracted', 0)}
  Searches Performed:      {service_stats.get('total_searches', 0)}

[yellow]API Usage:[/yellow]
  Embedding Requests:  {embedding_stats.get('total_requests', 0):,}
  Total Tokens:        {embedding_stats.get('total_tokens', 0):,}
  Cost (USD):          ${embedding_stats.get('total_cost_usd', 0):.4f}

[yellow]Storage:[/yellow]
  Database: PostgreSQL with pgvector
  User ID: {self.user_id}
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
                        await self.show_memories()

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
