#!/usr/bin/env python3
"""
Conversational AI Chatbot with Memory Integration.

This chatbot:
- Retrieves relevant memories from PostgreSQL when you chat
- Uses memories to provide personalized responses via OpenAI
- Creates new memories from your messages
- Shows what memories it's using in real-time
- Stores everything in the database with pgvector semantic search
- Exports clean memory JSON (without embeddings) for easy viewing

Run with:
    cd packages/backend
    poetry run python scripts/chatbot.py
"""

import asyncio
import uuid
import json
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from openai import AsyncOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import async_session_maker
from app.services.memory_service import MemoryService
from app.models.memory import MemoryType, Memory
from app.core.config import get_settings


console = Console()


class MemoryChatbot:
    """Conversational AI that uses database-backed memories to respond.

    This chatbot:
    1. Searches your PostgreSQL memories for relevant context
    2. Uses that context to provide personalized responses via OpenAI
    3. Extracts key facts from your messages
    4. Creates new memories in the database
    5. Exports clean JSON without embeddings for easy viewing
    6. Shows everything happening in real-time
    """

    def __init__(self, user_id: Optional[uuid.UUID] = None):
        """Initialize chatbot.

        Args:
            user_id: User ID (creates new if not provided)
        """
        self.console = console
        self.user_id = user_id or uuid.uuid4()
        self.settings = get_settings()

        # Initialize OpenAI client
        self.openai = AsyncOpenAI(api_key=self.settings.openai_api_key)

        # Conversation history for context
        self.conversation_history = []

        # Statistics
        self.messages_exchanged = 0
        self.memories_created = 0
        self.memories_retrieved = 0

        # Export path
        self.export_dir = Path("memory_exports")
        self.export_dir.mkdir(exist_ok=True)

    def show_header(self):
        """Display welcome header."""
        header = Panel(
            """[bold cyan]🤖 AI Chatbot with PostgreSQL Memory[/bold cyan]

[yellow]I'm an AI assistant with access to your personal memories stored in PostgreSQL.[/yellow]

[green]What I can do:[/green]
  💬 Have natural conversations with you
  🧠 Remember facts about you (stored in database)
  🔍 Search my memories using semantic similarity (pgvector)
  📝 Create new memories from our conversation
  📊 Show you which memories I'm using
  💾 Export clean JSON (without embeddings) for easy viewing

[yellow]Commands:[/yellow]
  💬 Just chat naturally!
  🔍 /search <query> - Search memories
  💾 /memories - View all memories
  📊 /stats - Show statistics
  📤 /export - Export memories to JSON
  🗑️  /clear - Clear conversation history
  ❓ /help - Show this help
  👋 /exit - Exit

[dim]All memories are stored in PostgreSQL with pgvector semantic search![/dim]
""",
            title="Welcome to Memory Chatbot",
            border_style="cyan",
            expand=False
        )
        self.console.print(header)
        self.console.print(f"\n[dim]User ID: {self.user_id}[/dim]")
        self.console.print(f"[dim]Export directory: {self.export_dir.absolute()}[/dim]\n")

    async def chat(self, message: str, db: AsyncSession):
        """Process message and respond.

        Args:
            message: User message
            db: Database session
        """
        self.messages_exchanged += 1
        memory_service = MemoryService(db)

        self.console.print("\n" + "─" * 70)
        self.console.print(f"[bold cyan]You:[/bold cyan] {message}")
        self.console.print("─" * 70)

        # Step 1: Search for relevant memories
        self.console.print("\n[dim]🔍 Searching PostgreSQL memories...[/dim]")
        relevant_memories = await memory_service.search_semantic(
            user_id=self.user_id,
            query_text=message,
            limit=5,
            threshold=0.5  # Lower threshold for more context
        )

        self.memories_retrieved += len(relevant_memories)

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

            for memory, score in relevant_memories:
                memory_table.add_row(
                    f"{score:.2f}",
                    memory.memory_type.value.upper(),
                    memory.content[:60] + ("..." if len(memory.content) > 60 else "")
                )

            self.console.print(memory_table)
        else:
            self.console.print("[dim]No relevant memories found[/dim]")

        # Step 2: Generate AI response using memories
        self.console.print("\n[dim]💭 Generating response using memories...[/dim]")
        response = await self._generate_response(message, relevant_memories)

        # Show response
        response_panel = Panel(
            response,
            title="🤖 Assistant",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(response_panel)

        # Step 3: Extract facts and create new memories
        self.console.print("\n[dim]📝 Extracting facts from your message...[/dim]")
        created_memories = await self._create_memories_from_message(message, db)

        if created_memories:
            # Show created memories
            creation_table = Table(
                title="✨ New Memories Created",
                box=box.SIMPLE,
                show_header=True,
                header_style="bold cyan"
            )
            creation_table.add_column("Memory", style="white", width=60)
            creation_table.add_column("Type", style="magenta")

            for memory in created_memories:
                creation_table.add_row(
                    memory.content,
                    memory.memory_type.value.upper()
                )

            self.console.print(creation_table)
            self.console.print(f"\n[green]✓ Created {len(created_memories)} new memories in database[/green]")
            self.memories_created += len(created_memories)
        else:
            self.console.print("[dim]No new facts to memorize[/dim]")

    async def _generate_response(
        self,
        message: str,
        relevant_memories: List[tuple[Memory, float]]
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
                memory_context += f"- [{memory.memory_type.value}] {memory.content}\n"

        # Build system prompt
        system_prompt = f"""You are a helpful AI assistant with access to the user's personal memories stored in a database.

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
            model="gpt-4o-mini",
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

    async def _create_memories_from_message(
        self,
        message: str,
        db: AsyncSession
    ) -> List[Memory]:
        """Extract facts and create memories from message.

        Args:
            message: User message
            db: Database session

        Returns:
            List of created memories
        """
        memory_service = MemoryService(db)

        # Use GPT to extract facts
        extraction_prompt = f"""Extract key facts from this message that should be remembered.

Message: "{message}"

Return a JSON array of facts. Each fact should be:
- A clear, standalone statement
- Something worth remembering long-term
- In third person (e.g., "User prefers...", "User is working on...")

Return ONLY the JSON array, no other text. If no facts to extract, return [].

Example: ["User is studying computer science", "User prefers working in the morning"]"""

        response = await self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0.3,
            max_tokens=300
        )

        try:
            facts_text = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if facts_text.startswith("```"):
                facts_text = facts_text.split("```")[1]
                if facts_text.startswith("json"):
                    facts_text = facts_text[4:]
                facts_text = facts_text.strip()

            facts = json.loads(facts_text)

            if not isinstance(facts, list):
                return []

            created_memories = []

            for fact in facts:
                if not fact or not isinstance(fact, str):
                    continue

                # Determine memory type based on content
                fact_lower = fact.lower()
                if any(word in fact_lower for word in ["prefer", "like", "hate", "always", "never", "personality"]):
                    memory_type = MemoryType.PERSONAL
                elif any(word in fact_lower for word in ["working on", "goal", "project", "plan"]):
                    memory_type = MemoryType.PROJECT
                else:
                    memory_type = MemoryType.TASK

                # Create memory
                memory = await memory_service.create_memory(
                    user_id=self.user_id,
                    content=fact,
                    memory_type=memory_type,
                    extra_data={
                        "source_message": message,
                        "created_at": datetime.now().isoformat()
                    }
                )

                created_memories.append(memory)

            return created_memories

        except json.JSONDecodeError:
            return []
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not extract facts: {e}[/yellow]")
            return []

    async def search_memories(self, query: str, db: AsyncSession):
        """Search and display memories.

        Args:
            query: Search query
            db: Database session
        """
        memory_service = MemoryService(db)

        self.console.print(f"\n[cyan]🔍 Searching: \"{query}\"[/cyan]\n")

        results = await memory_service.search_semantic(
            user_id=self.user_id,
            query_text=query,
            limit=10,
            threshold=0.4
        )

        if results:
            results_table = Table(title="Search Results", box=box.ROUNDED)
            results_table.add_column("Score", style="green", width=8)
            results_table.add_column("Type", style="cyan", width=10)
            results_table.add_column("Content", style="white")

            for memory, score in results:
                results_table.add_row(
                    f"{score:.3f}",
                    memory.memory_type.value.upper(),
                    memory.content
                )

            self.console.print(results_table)
        else:
            self.console.print("[yellow]No results found[/yellow]")

    async def show_memories(self, db: AsyncSession):
        """Show all user memories.

        Args:
            db: Database session
        """
        memory_service = MemoryService(db)
        memories = await memory_service.get_user_memories(self.user_id, limit=100)

        if not memories:
            self.console.print("\n[dim]No memories yet[/dim]")
            return

        self.console.print(f"\n[cyan]💾 Your Memories ({len(memories)} total)[/cyan]\n")

        memory_table = Table(title="All Memories", box=box.ROUNDED)
        memory_table.add_column("Time", style="dim", width=19)
        memory_table.add_column("Type", style="magenta", width=10)
        memory_table.add_column("Content", style="white", width=50)

        for memory in memories[:20]:  # Show last 20
            time_str = memory.created_at.strftime("%Y-%m-%d %H:%M:%S")

            memory_table.add_row(
                time_str,
                memory.memory_type.value.upper(),
                memory.content
            )

        self.console.print(memory_table)

        if len(memories) > 20:
            self.console.print(f"\n[dim]... and {len(memories) - 20} more[/dim]")

    async def export_memories(self, db: AsyncSession):
        """Export memories to clean JSON file.

        Args:
            db: Database session
        """
        memory_service = MemoryService(db)

        self.console.print("\n[cyan]📤 Exporting memories...[/cyan]")

        # Export without embeddings for readability
        export_json = await memory_service.export_memories(
            user_id=self.user_id,
            include_embeddings=False
        )

        # Save to file
        export_path = self.export_dir / f"memories_{self.user_id}_clean.json"
        export_path.write_text(export_json)

        self.console.print(f"[green]✓ Exported to: {export_path.absolute()}[/green]")

        # Show preview
        data = json.loads(export_json)
        self.console.print(f"\n[dim]Total memories: {data['total_memories']}[/dim]")

    async def show_statistics(self, db: AsyncSession):
        """Show usage statistics.

        Args:
            db: Database session
        """
        memory_service = MemoryService(db)
        stats = await memory_service.get_memory_stats(self.user_id)

        stats_panel = Panel(
            f"""[bold cyan]📊 Session Statistics[/bold cyan]

[yellow]Conversation:[/yellow]
  Messages Exchanged:  {self.messages_exchanged}
  Memories Created:    {self.memories_created}
  Memories Retrieved:  {self.memories_retrieved}

[yellow]Database Storage:[/yellow]
  Total Memories:      {stats['total_memories']}
  Personal Memories:   {stats['by_type']['personal']}
  Project Memories:    {stats['by_type']['project']}
  Task Memories:       {stats['by_type']['task']}
  With Embeddings:     {stats['memories_with_embeddings']}

[yellow]API Usage:[/yellow]
  Embedding Requests:  {stats['embedding_stats']['total_requests']}
  Total Tokens:        {stats['embedding_stats']['total_tokens']:,}
  Cost (USD):          ${stats['embedding_stats']['total_cost_usd']:.4f}

[yellow]Export:[/yellow]
  Directory: {self.export_dir.absolute()}
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

                # Create DB session for this interaction
                async with async_session_maker() as db:
                    # Handle commands
                    if user_input.startswith("/"):
                        command = user_input[1:].lower()

                        if command in ["exit", "quit"]:
                            self.console.print("\n[bold]👋 Goodbye! Your memories are saved in PostgreSQL.[/bold]\n")
                            break

                        elif command == "help":
                            self.show_header()

                        elif command == "stats":
                            await self.show_statistics(db)

                        elif command == "memories":
                            await self.show_memories(db)

                        elif command == "export":
                            await self.export_memories(db)

                        elif command == "clear":
                            self.conversation_history = []
                            self.console.print("\n[green]✓ Conversation history cleared[/green]")

                        elif command.startswith("search "):
                            query = command[7:].strip()
                            if query:
                                await self.search_memories(query, db)
                            else:
                                self.console.print("[yellow]Usage: /search <query>[/yellow]")

                        else:
                            self.console.print(f"[yellow]Unknown command: {command}[/yellow]")
                            self.console.print("[dim]Type /help for commands[/dim]")

                    else:
                        # Chat!
                        await self.chat(user_input, db)

            except KeyboardInterrupt:
                self.console.print("\n\n[bold]👋 Goodbye![/bold]\n")
                break

            except Exception as e:
                self.console.print(f"\n[red]❌ Error: {e}[/red]")
                import traceback
                traceback.print_exc()


async def main():
    """Main entry point."""
    console.print("\n[cyan]Connecting to database...[/cyan]")

    # Test database connection
    try:
        async with async_session_maker() as db:
            # Simple query to test connection
            result = await db.execute("SELECT 1")
            result.scalar()
            console.print("[green]✓ Database connected![/green]\n")
    except Exception as e:
        console.print(f"[red]❌ Database connection failed: {e}[/red]")
        console.print("\n[yellow]Make sure:[/yellow]")
        console.print("  1. Supabase is running")
        console.print("  2. DATABASE_URL is set in .env")
        console.print("  3. Migrations are applied: poetry run alembic upgrade head")
        return

    chatbot = MemoryChatbot()
    await chatbot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\n[bold]👋 Goodbye![/bold]\n")
