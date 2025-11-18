"""
Integration of workflow system with Delight's core features.
Shows how workflows orchestrate Memory, Companions, Missions, and Emotions.
"""

from typing import Any
from uuid import UUID
from datetime import datetime

# ============================================================================
# INTEGRATION 1: Memory-Aware Workflows
# ============================================================================

class MemoryIntegratedWorkflow:
    """
    Workflows that leverage semantic memory for context-aware execution.

    Use Cases:
    - Learning workflows query past learning sessions for continuity
    - Stress management workflows analyze historical stressor patterns
    - Goal workflows reference past attempts to avoid repeated failures
    """

    async def execute_with_memory_context(
        self,
        workflow_id: UUID,
        user_id: UUID,
        execution_context: dict[str, Any]
    ):
        """
        Execute workflow with memory-informed decision making.
        """
        # STEP 1: Query relevant memories before starting
        memories = await self.get_relevant_memories(
            user_id=user_id,
            workflow_type=execution_context.get('workflow_type'),
            query=execution_context.get('goal')
        )

        # STEP 2: Inject memory context into workflow
        execution_context['historical_context'] = {
            'relevant_memories': memories,
            'past_attempts': self._extract_past_attempts(memories),
            'learned_lessons': self._extract_lessons(memories),
            'user_preferences': self._extract_preferences(memories)
        }

        # STEP 3: Execute workflow with enriched context
        # Workflow nodes can reference context['historical_context']

        # STEP 4: Create memories from workflow execution
        await self.create_workflow_memory(
            user_id=user_id,
            workflow_id=workflow_id,
            execution_summary={
                'goal': execution_context.get('goal'),
                'outcome': 'success',  # or 'failure'
                'key_insights': [],
                'emotional_state': execution_context.get('emotion')
            }
        )

    async def get_relevant_memories(
        self,
        user_id: UUID,
        workflow_type: str,
        query: str,
        limit: int = 10
    ) -> list[dict]:
        """Query semantic memories relevant to current workflow."""
        # Example: Memory service with vector search
        from app.services.memory_service import MemoryService

        memory_service = MemoryService()

        # Semantic search for relevant past experiences
        memories = await memory_service.semantic_search(
            user_id=user_id,
            query=f"Past experiences with {query} and {workflow_type}",
            limit=limit,
            filters={'workflow_related': True}
        )

        return memories

    def _extract_past_attempts(self, memories: list) -> dict:
        """Extract what user tried before."""
        attempts = []
        for memory in memories:
            if 'workflow_execution' in memory.get('metadata', {}):
                attempts.append({
                    'date': memory['created_at'],
                    'approach': memory['metadata']['approach'],
                    'outcome': memory['metadata']['outcome'],
                    'why_failed': memory['metadata'].get('failure_reason')
                })
        return {'count': len(attempts), 'attempts': attempts}

    def _extract_lessons(self, memories: list) -> list[str]:
        """Extract lessons learned from past experiences."""
        lessons = []
        for memory in memories:
            if 'lesson' in memory.get('content', ''):
                lessons.append(memory['content'])
        return lessons

    def _extract_preferences(self, memories: list) -> dict:
        """Infer user preferences from memory patterns."""
        # Example: User prefers morning workouts, visual learning, etc.
        return {
            'preferred_time': 'morning',
            'learning_style': 'visual',
            'motivation_style': 'progress_tracking'
        }


# ============================================================================
# INTEGRATION 2: Multi-Persona Workflows
# ============================================================================

class PersonaOrchstratedWorkflow:
    """
    Workflows where different AI personas handle different nodes.

    Use Cases:
    - Goal planning: Coach persona motivates → Analyst persona plans → Therapist handles blockers
    - Learning: Teacher persona instructs → Mentor persona guides → Critic persona reviews
    - Writing: Creative persona drafts → Editor persona refines → Publisher persona promotes
    """

    PERSONA_SPECIALIZATIONS = {
        'coach': ['motivation', 'goal_setting', 'accountability'],
        'therapist': ['emotional_processing', 'stress_management', 'cognitive_reframing'],
        'analyst': ['data_analysis', 'planning', 'optimization'],
        'creative': ['brainstorming', 'writing', 'ideation'],
        'mentor': ['guidance', 'skill_development', 'feedback'],
    }

    async def assign_personas_to_nodes(
        self,
        workflow: dict,
        user_preferences: dict | None = None
    ) -> dict:
        """
        Automatically assign best persona to each workflow node.
        """
        for node in workflow['nodes']:
            node_type = node.get('node_type')
            task_keywords = node.get('name', '').lower()

            # Determine best persona based on task
            if 'motivate' in task_keywords or 'encourage' in task_keywords:
                node['assigned_persona'] = 'coach'
            elif 'plan' in task_keywords or 'analyze' in task_keywords:
                node['assigned_persona'] = 'analyst'
            elif 'feel' in task_keywords or 'emotion' in task_keywords:
                node['assigned_persona'] = 'therapist'
            elif 'creative' in task_keywords or 'brainstorm' in task_keywords:
                node['assigned_persona'] = 'creative'
            else:
                # Default to user's favorite persona
                node['assigned_persona'] = user_preferences.get('favorite_persona', 'coach')

        return workflow

    async def execute_node_with_persona(
        self,
        node: dict,
        context: dict,
        persona_id: str
    ) -> dict:
        """
        Execute node using specified persona's voice and expertise.
        """
        # Load persona configuration
        persona_config = await self.get_persona_config(persona_id)

        # Execute with persona-specific prompts and behavior
        prompt = self._build_persona_prompt(
            persona=persona_config,
            task=node['name'],
            context=context
        )

        # Use persona's model preferences and temperature
        result = await self._call_llm(
            prompt=prompt,
            model=persona_config.get('preferred_model', 'gpt-4o-mini'),
            temperature=persona_config.get('temperature', 0.7),
            system_message=persona_config['system_message']
        )

        return result


# ============================================================================
# INTEGRATION 3: Mission-Generating Workflows
# ============================================================================

class MissionGeneratingWorkflow:
    """
    Workflows that automatically create daily missions from long-term goals.

    Use Cases:
    - "Lose 20 pounds" workflow generates daily mission: "Log meals and 30min cardio"
    - "Learn Python" workflow generates daily mission: "Complete 2 coding exercises"
    - "Reduce stress" workflow generates daily mission: "10min meditation + gratitude journal"
    """

    async def generate_daily_mission(
        self,
        workflow_execution: dict,
        current_progress: dict
    ) -> dict:
        """
        Generate today's mission based on workflow progress.
        """
        # Determine current phase of workflow
        completed_nodes = [n for n in workflow_execution['nodes'] if n['status'] == 'completed']
        current_phase = self._determine_phase(completed_nodes, workflow_execution['total_nodes'])

        # Adjust difficulty based on user's success rate
        success_rate = current_progress.get('success_rate', 0.5)
        difficulty = self._calculate_difficulty(current_phase, success_rate)

        # Generate mission
        mission = {
            'title': self._generate_mission_title(workflow_execution, current_phase),
            'description': self._generate_mission_description(workflow_execution, current_phase),
            'difficulty': difficulty,
            'estimated_duration': self._estimate_duration(current_phase),
            'type': 'workflow_generated',
            'workflow_id': workflow_execution['workflow_id'],
            'workflow_node_id': workflow_execution['current_node_id'],
            'success_criteria': self._define_success_criteria(current_phase),
        }

        return mission

    def _determine_phase(self, completed_nodes: list, total_nodes: int) -> str:
        """Determine what phase of workflow we're in."""
        progress_pct = len(completed_nodes) / total_nodes if total_nodes > 0 else 0

        if progress_pct < 0.25:
            return 'foundation'  # Building habits, gathering resources
        elif progress_pct < 0.50:
            return 'development'  # Active skill building
        elif progress_pct < 0.75:
            return 'mastery'  # Refinement and practice
        else:
            return 'maintenance'  # Sustaining gains

    def _calculate_difficulty(self, phase: str, success_rate: float) -> int:
        """Calculate appropriate mission difficulty (1-5)."""
        base_difficulty = {
            'foundation': 1,
            'development': 2,
            'mastery': 3,
            'maintenance': 2
        }[phase]

        # Adjust based on user's success
        if success_rate > 0.8:
            return min(5, base_difficulty + 1)  # Increase challenge
        elif success_rate < 0.5:
            return max(1, base_difficulty - 1)  # Decrease challenge
        else:
            return base_difficulty


# ============================================================================
# INTEGRATION 4: Emotion-Aware Workflows
# ============================================================================

class EmotionAdaptiveWorkflow:
    """
    Workflows that adapt based on user's emotional state.

    Use Cases:
    - If user logs "anxious" → workflow offers gentler alternative path
    - If user logs "motivated" → workflow suggests accelerated path
    - If user logs "frustrated" → workflow pauses and offers support
    """

    async def adapt_workflow_to_emotion(
        self,
        workflow_execution: dict,
        current_emotion: dict
    ) -> dict:
        """
        Modify workflow path based on user's emotional state.
        """
        emotion_type = current_emotion.get('emotion')
        intensity = current_emotion.get('intensity', 0.5)

        # Get current node and next planned nodes
        current_node_id = workflow_execution['current_node_id']
        next_nodes = self._get_next_nodes(workflow_execution, current_node_id)

        # Apply emotion-based adaptations
        if emotion_type in ['anxious', 'stressed', 'overwhelmed']:
            # Reduce cognitive load
            adaptations = {
                'reduce_complexity': True,
                'add_support_nodes': True,
                'extend_deadlines': True,
                'suggested_message': "I notice you're feeling stressed. Let's take it slower today."
            }

        elif emotion_type in ['motivated', 'energized', 'confident']:
            # Increase challenge
            adaptations = {
                'increase_complexity': True,
                'add_stretch_goals': True,
                'suggested_message': "You're on fire! Want to tackle something more ambitious?"
            }

        elif emotion_type in ['frustrated', 'discouraged', 'sad']:
            # Add emotional support
            adaptations = {
                'add_reflection_node': True,
                'add_encouragement': True,
                'offer_alternative_approach': True,
                'suggested_message': "This is tough, but you're making progress. Want to try a different approach?"
            }

        else:
            # No adaptation needed
            adaptations = {'continue_as_planned': True}

        return adaptations


# ============================================================================
# INTEGRATION 5: Stressor Log Integration
# ============================================================================

class StressorWorkflowIntegration:
    """
    Workflows triggered by or informed by stressor logs.

    Use Cases:
    - When user logs "work stress" → trigger work-life balance workflow
    - Analyze stressor patterns → generate personalized stress management workflow
    - Track stress reduction over workflow execution
    """

    async def trigger_workflow_from_stressor(
        self,
        stressor_log: dict,
        user_id: UUID
    ) -> UUID | None:
        """
        Automatically trigger appropriate workflow when stressor logged.
        """
        stressor_type = stressor_log.get('category')
        intensity = stressor_log.get('intensity')

        # Map stressor types to workflows
        STRESSOR_WORKFLOWS = {
            'work': 'work_life_balance_workflow',
            'relationship': 'communication_skills_workflow',
            'health': 'wellness_routine_workflow',
            'financial': 'financial_planning_workflow',
            'sleep': 'sleep_hygiene_workflow',
        }

        # Only trigger for high intensity stressors
        if intensity >= 7 and stressor_type in STRESSOR_WORKFLOWS:
            workflow_template = STRESSOR_WORKFLOWS[stressor_type]

            # Create workflow instance
            workflow_id = await self.instantiate_workflow(
                template_name=workflow_template,
                user_id=user_id,
                context={'trigger_stressor': stressor_log}
            )

            return workflow_id

        return None

    async def analyze_stressor_patterns(
        self,
        user_id: UUID,
        lookback_days: int = 30
    ) -> dict:
        """
        Analyze stressor patterns to recommend workflows.
        """
        # Get stressor logs
        stressor_logs = await self.get_stressor_logs(user_id, lookback_days)

        # Pattern analysis
        patterns = {
            'most_common_stressors': self._find_common_stressors(stressor_logs),
            'peak_stress_times': self._find_stress_timing(stressor_logs),
            'stress_triggers': self._identify_triggers(stressor_logs),
            'effective_coping': self._identify_what_works(stressor_logs),
        }

        # Generate personalized workflow
        workflow_plan = await self._generate_stress_management_workflow(patterns)

        return workflow_plan


# ============================================================================
# INTEGRATION 6: Complete Example - Goal to Daily Missions
# ============================================================================

class GoalToMissionPipeline:
    """
    End-to-end integration: User goal → Workflow plan → Daily missions.

    Example Flow:
    1. User: "I want to lose 20 pounds"
    2. System generates multi-week workflow with phases
    3. Each day, workflow generates contextual mission
    4. Mission completion updates workflow state
    5. Workflow adapts based on progress and emotions
    6. Memories capture learnings for future
    """

    async def process_user_goal(
        self,
        user_id: UUID,
        goal: str,
        timeframe_weeks: int = 12
    ) -> dict:
        """
        Complete pipeline from goal to executable workflow.
        """
        # STEP 1: Generate workflow plan using LLM
        from app.services.workflow_planner import WorkflowPlanner

        planner = WorkflowPlanner(db=self.db)
        workflow, summary = await planner.generate_workflow_plan(
            user_id=user_id,
            user_query=goal,
            context={'timeframe_weeks': timeframe_weeks}
        )

        # STEP 2: Enhance with memory context
        memory_workflow = MemoryIntegratedWorkflow()
        memories = await memory_workflow.get_relevant_memories(
            user_id=user_id,
            workflow_type='goal_achievement',
            query=goal
        )

        # STEP 3: Assign personas to nodes
        persona_workflow = PersonaOrchstratedWorkflow()
        workflow_dict = await persona_workflow.assign_personas_to_nodes(
            workflow={'nodes': workflow.nodes, 'edges': workflow.edges}
        )

        # STEP 4: Set up mission generation
        mission_gen = MissionGeneratingWorkflow()

        # STEP 5: Create execution with all integrations
        execution_config = {
            'workflow_id': workflow.id,
            'user_id': user_id,
            'goal': goal,
            'historical_context': memories,
            'persona_assignments': workflow_dict,
            'mission_generation_enabled': True,
            'emotion_adaptation_enabled': True,
        }

        return {
            'workflow': workflow,
            'summary': summary,
            'execution_config': execution_config,
            'first_mission': await mission_gen.generate_daily_mission(
                workflow_execution={'nodes': [], 'total_nodes': len(workflow.nodes)},
                current_progress={'success_rate': 1.0}  # Start optimistic
            )
        }
