from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, and_, desc, update
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import asyncio
import logging

from app.models.discussion import Discussion
from app.models.participant import DiscussionParticipant
from app.models.message import DiscussionMessage
from app.models.topic import Topic
from app.models.character import Character
from app.schemas.discussion import DiscussionCreate, DiscussionUpdate, DiscussionControl
from app.services.llm_orchestrator import LLMOrchestrator
from app.core.redis import CacheService

logger = logging.getLogger(__name__)


class DiscussionEngineService:
    """Service for orchestrating multi-character discussions"""

    # Discussion phases and their prompts
    PHASES = {
        "opening": "Introduce yourself and state your initial position on the topic.",
        "development": "Respond to previous points, deepen your arguments, and explore the topic.",
        "debate": "Engage with opposing viewpoints, debate key disagreements.",
        "closing": "Summarize your position and attempt to find common ground or clarify differences."
    }

    # Track running discussions
    _running_tasks: Dict[UUID, asyncio.Task] = {}

    def __init__(self, db: AsyncSession, llm_orchestrator: LLMOrchestrator, cache: CacheService, session_factory: async_sessionmaker = None):
        self.db = db
        self.llm_orchestrator = llm_orchestrator
        self.cache = cache
        self.session_factory = session_factory

    async def get_discussion_by_id(
        self,
        discussion_id: UUID,
        user_id: UUID
    ) -> Optional[Discussion]:
        """Get discussion by ID (ensuring user owns it)"""
        from sqlalchemy.orm import with_loader_criteria

        result = await self.db.execute(
            select(Discussion).where(
                and_(
                    Discussion.id == discussion_id,
                    Discussion.user_id == user_id
                )
            ).execution_options(populate_existing=True)
        )
        discussion = result.scalar_one_or_none()

        # Ensure all attributes are loaded by accessing them
        if discussion:
            _ = discussion.id, discussion.topic_id, discussion.user_id
            _ = discussion.discussion_mode, discussion.max_rounds, discussion.status
            _ = discussion.current_round, discussion.current_phase
            _ = discussion.llm_provider, discussion.llm_model
            _ = discussion.total_tokens_used, discussion.estimated_cost_usd
            _ = discussion.started_at, discussion.completed_at
            _ = discussion.created_at, discussion.updated_at

        return discussion

    async def create_discussion(
        self,
        user_id: UUID,
        discussion_data: DiscussionCreate
    ) -> Discussion:
        """Create new discussion"""
        # Verify topic exists and belongs to user
        topic_result = await self.db.execute(
            select(Topic).where(
                and_(
                    Topic.id == discussion_data.topic_id,
                    Topic.user_id == user_id
                )
            )
        )
        topic = topic_result.scalar_one_or_none()
        if not topic:
            raise ValueError("Topic not found")

        # Verify characters exist
        character_ids = discussion_data.character_ids
        characters_result = await self.db.execute(
            select(Character).where(Character.id.in_(character_ids))
        )
        characters = list(characters_result.scalars().all())

        if len(characters) != len(character_ids):
            raise ValueError("Some characters not found")

        if not (3 <= len(characters) <= 7):
            raise ValueError("Discussion must have 3-7 characters")

        # Create discussion
        discussion = Discussion(
            topic_id=discussion_data.topic_id,
            user_id=user_id,
            discussion_mode=discussion_data.discussion_mode,
            max_rounds=discussion_data.max_rounds,
            status="initialized",
            current_round=0,
            current_phase="opening"
        )
        self.db.add(discussion)
        await self.db.flush()

        # Create participants
        for idx, character in enumerate(characters):
            participant = DiscussionParticipant(
                discussion_id=discussion.id,
                character_id=character.id,
                position=idx,
                stance=character.config.get("stance", "neutral")
            )
            self.db.add(participant)

        # Update topic status
        topic.status = "in_discussion"

        await self.db.commit()
        await self.db.refresh(discussion)

        # Cache discussion state
        await self._cache_discussion_state(discussion)

        return discussion

    async def start_discussion(
        self,
        discussion_id: UUID,
        user_id: UUID,
        provider_name: str = "openai"
    ) -> Discussion:
        """Start a discussion"""
        discussion = await self.get_discussion_by_id(discussion_id, user_id)
        if not discussion:
            raise ValueError("Discussion not found")

        if discussion.status != "initialized":
            raise ValueError(f"Discussion is not in initialized state: {discussion.status}")

        # Get LLM provider
        provider = self.llm_orchestrator.get_provider(provider_name)
        if not provider:
            raise ValueError(f"LLM provider not found: {provider_name}")

        # Update discussion
        discussion.status = "running"
        discussion.started_at = datetime.utcnow()
        discussion.llm_provider = provider_name
        await self.db.commit()

        # Refresh to ensure all fields are loaded from database
        await self.db.refresh(discussion)

        # Cache discussion state (do this before starting background task)
        await self._cache_discussion_state(discussion)

        # Start background task to run discussion (with its own session)
        # Don't await it - let it run in background
        if discussion_id not in self._running_tasks or self._running_tasks[discussion_id].done():
            if not self.session_factory:
                logger.warning(f"No session factory provided, background task may fail for discussion {discussion_id}")
            # Don't use asyncio.create_task here - it will be scheduled automatically
            # Just return and let the task run
            logger.info(f"Creating background task for discussion {discussion_id}")
            task = asyncio.create_task(self._run_discussion_loop(discussion_id, provider_name))
            self._running_tasks[discussion_id] = task
            logger.info(f"Background task created and stored for discussion {discussion_id}, task done: {task.done()}")

        # Return the discussion - it's still attached to session but that's OK
        # FastAPI will handle the session cleanup after response is sent
        return discussion

    async def pause_discussion(
        self,
        discussion_id: UUID,
        user_id: UUID
    ) -> Discussion:
        """Pause a running discussion"""
        discussion = await self.get_discussion_by_id(discussion_id, user_id)
        if not discussion:
            raise ValueError("Discussion not found")

        if discussion.status != "running":
            raise ValueError(f"Cannot pause discussion in status: {discussion.status}")

        discussion.status = "paused"

        # Note: Background task will check status and stop on next iteration
        # We don't cancel the task immediately to allow graceful shutdown

        await self.db.commit()

        # Refresh to ensure all fields are loaded from database
        await self.db.refresh(discussion)

        await self._cache_discussion_state(discussion)

        return discussion

    async def resume_discussion(
        self,
        discussion_id: UUID,
        user_id: UUID
    ) -> Discussion:
        """Resume a paused discussion"""
        discussion = await self.get_discussion_by_id(discussion_id, user_id)
        if not discussion:
            raise ValueError("Discussion not found")

        if discussion.status != "paused":
            raise ValueError("Discussion is not paused")

        discussion.status = "running"
        await self.db.commit()

        # Refresh to ensure all fields are loaded from database
        await self.db.refresh(discussion)

        await self._cache_discussion_state(discussion)

        return discussion

    async def stop_discussion(
        self,
        discussion_id: UUID,
        user_id: UUID
    ) -> Discussion:
        """Stop a discussion (end it early)"""
        discussion = await self.get_discussion_by_id(discussion_id, user_id)
        if not discussion:
            raise ValueError("Discussion not found")

        # Allow stopping from various states (initialized, running, paused)
        # But not from already completed or failed states
        if discussion.status in ["completed", "failed"]:
            raise ValueError(f"Discussion is already {discussion.status}")

        # Cancel background task if running
        if discussion_id in self._running_tasks:
            task = self._running_tasks[discussion_id]
            if not task.done():
                task.cancel()
            del self._running_tasks[discussion_id]
            logger.info(f"Cancelled background task for discussion {discussion_id}")

        discussion.status = "completed"
        discussion.completed_at = datetime.utcnow()

        # Update topic status
        topic_result = await self.db.execute(
            select(Topic).where(Topic.id == discussion.topic_id)
        )
        topic = topic_result.scalar_one_or_none()
        if topic:
            topic.status = "completed"

        await self.db.commit()

        # Refresh to ensure all fields are loaded from database
        await self.db.refresh(discussion)

        await self._cache_discussion_state(discussion)

        return discussion

    async def inject_question(
        self,
        discussion_id: UUID,
        user_id: UUID,
        question: str
    ) -> DiscussionMessage:
        """Inject a user question into the discussion"""
        discussion = await self.get_discussion_by_id(discussion_id, user_id)
        if not discussion:
            raise ValueError("Discussion not found")

        if discussion.status != "running":
            raise ValueError("Discussion is not running")

        # Create message with user-injected question
        message = DiscussionMessage(
            discussion_id=discussion.id,
            participant_id=UUID("00000000-0000-0000-0000-000000000000"),  # Special ID for user questions
            round=discussion.current_round,
            phase=discussion.current_phase,
            content=question,
            token_count=0,
            is_injected_question=True
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def get_user_discussions(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[Discussion]:
        """Get discussions for a user"""
        result = await self.db.execute(
            select(Discussion)
            .where(Discussion.user_id == user_id)
            .order_by(desc(Discussion.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_discussion_messages(
        self,
        discussion_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[DiscussionMessage]:
        """Get messages for a discussion"""
        # Verify user owns discussion
        discussion = await self.get_discussion_by_id(discussion_id, user_id)
        if not discussion:
            raise ValueError("Discussion not found")

        result = await self.db.execute(
            select(DiscussionMessage)
            .where(DiscussionMessage.discussion_id == discussion_id)
            .order_by(DiscussionMessage.created_at)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_discussion_state(
        self,
        discussion_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get current discussion state from cache or database"""
        cache_key = f"discussion_state:{discussion_id}"
        state = await self.cache.get(cache_key)

        if state:
            return state

        # Fallback to database
        result = await self.db.execute(
            select(Discussion).where(Discussion.id == discussion_id)
        )
        discussion = result.scalar_one_or_none()
        if not discussion:
            return None

        # Calculate progress including phases
        phases = list(self.PHASES.keys())
        current_phase_index = phases.index(discussion.current_phase) if discussion.current_phase in phases else 0
        total_phases = len(phases)
        phase_progress = current_phase_index / total_phases
        progress_percentage = ((discussion.current_round + phase_progress) / discussion.max_rounds * 100) if discussion.max_rounds > 0 else 0

        return {
            "id": str(discussion.id),
            "status": discussion.status,
            "current_round": discussion.current_round,
            "max_rounds": discussion.max_rounds,
            "current_phase": discussion.current_phase,
            "progress_percentage": min(progress_percentage, 100)
        }

    async def _cache_discussion_state(self, discussion: Discussion):
        """Cache discussion state"""
        # Calculate progress including phases (each round has 4 phases)
        phases = list(self.PHASES.keys())
        current_phase_index = phases.index(discussion.current_phase) if discussion.current_phase in phases else 0

        # Progress = (completed rounds + current phase index / total phases) / total rounds
        total_phases = len(phases)
        phase_progress = current_phase_index / total_phases
        round_progress = discussion.current_round / discussion.max_rounds if discussion.max_rounds > 0 else 0

        # Combined progress
        progress_percentage = ((discussion.current_round + phase_progress) / discussion.max_rounds * 100) if discussion.max_rounds > 0 else 0

        state = {
            "id": str(discussion.id),
            "status": discussion.status,
            "current_round": discussion.current_round,
            "max_rounds": discussion.max_rounds,
            "current_phase": discussion.current_phase,
            "progress_percentage": min(progress_percentage, 100)  # Cap at 100%
        }

        cache_key = f"discussion_state:{discussion.id}"
        # Cache for 1 hour or until discussion completes
        ttl = 3600 if discussion.status == "running" else 86400
        await self.cache.set(cache_key, state, ttl=ttl)

    async def _run_discussion_loop(self, discussion_id: UUID, provider_name: str):
        """Run the discussion loop in background"""
        logger.info(f"Starting discussion loop for {discussion_id}")

        # Create a new session for the background task
        if not self.session_factory:
            logger.error(f"No session factory available for discussion {discussion_id}")
            return

        logger.info(f"Session factory confirmed for discussion {discussion_id}")

        async with self.session_factory() as db:
            logger.info(f"Database session created for discussion {discussion_id}")
            try:
                iteration = 0
                while True:
                    iteration += 1
                    logger.info(f"Discussion {discussion_id}: Starting iteration {iteration}")
                    # Refresh discussion from database
                    result = await db.execute(
                        select(Discussion).where(Discussion.id == discussion_id)
                    )
                    discussion = result.scalar_one_or_none()

                    if not discussion:
                        logger.warning(f"Discussion {discussion_id} not found, stopping loop")
                        break

                    # Check if discussion is still running
                    if discussion.status != "running":
                        logger.info(f"Discussion {discussion_id} status is {discussion.status}, stopping loop")
                        break

                    # Check if discussion is complete
                    if discussion.current_round >= discussion.max_rounds:
                        logger.info(f"Discussion {discussion_id} reached max rounds, completing")
                        discussion.status = "completed"
                        discussion.completed_at = datetime.utcnow()
                        await db.commit()
                        await self._cache_discussion_state(discussion)
                        break

                    # Get participants
                    participants_result = await db.execute(
                        select(DiscussionParticipant, Character)
                        .join(Character, DiscussionParticipant.character_id == Character.id)
                        .where(DiscussionParticipant.discussion_id == discussion_id)
                        .order_by(DiscussionParticipant.position)
                    )
                    participants = participants_result.all()

                    if not participants:
                        logger.error(f"No participants found for discussion {discussion_id}")
                        break

                    # Get topic
                    topic_result = await db.execute(
                        select(Topic).where(Topic.id == discussion.topic_id)
                    )
                    topic = topic_result.scalar_one_or_none()

                    if not topic:
                        logger.error(f"Topic not found for discussion {discussion_id}")
                        break

                    # Generate messages for each participant in this round
                    for participant, character in participants:
                        # Check if discussion is still running
                        result = await db.execute(
                            select(Discussion).where(Discussion.id == discussion_id)
                        )
                        current_discussion = result.scalar_one_or_none()
                        if not current_discussion or current_discussion.status != "running":
                            logger.info(f"Discussion {discussion_id} stopped during message generation")
                            return

                        logger.info(f"Generating message for {character.name} in round {discussion.current_round}, phase {discussion.current_phase}")

                        # Generate message for this participant
                        try:
                            message = await self._generate_message(
                                db, discussion, participant, character, topic, provider_name
                            )
                            logger.info(f"Generated message for {character.name} in round {discussion.current_round}")

                            # Small delay between messages to simulate natural conversation
                            await asyncio.sleep(2)

                        except Exception as e:
                            logger.error(f"Error generating message for {character.name}: {e}")
                            # Continue with next participant
                            continue

                    # Move to next phase/round
                    await self._advance_discussion(db, discussion)

                    # Refresh discussion after advance
                    result = await db.execute(
                        select(Discussion).where(Discussion.id == discussion_id)
                    )
                    discussion = result.scalar_one_or_none()

                    if discussion and discussion.status == "running":
                        # Delay between rounds
                        await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error in discussion loop for {discussion_id}: {e}")
                # Try to mark discussion as failed
                try:
                    result = await db.execute(
                        select(Discussion).where(Discussion.id == discussion_id)
                    )
                    discussion = result.scalar_one_or_none()
                    if discussion and discussion.status == "running":
                        discussion.status = "failed"
                        await db.commit()
                        await self._cache_discussion_state(discussion)
                except Exception as e2:
                    logger.error(f"Failed to mark discussion as failed: {e2}")
            finally:
                # Clean up task reference
                if discussion_id in self._running_tasks:
                    del self._running_tasks[discussion_id]
                logger.info(f"Discussion loop for {discussion_id} ended")

    async def _summarize_round_messages(
        self,
        db: AsyncSession,
        discussion: Discussion,
        round_messages: dict,
        round_num: int,
        provider_name: str
    ) -> str:
        """Summarize messages from a round using LLM with caching"""
        import json
        import hashlib

        # Create a cache key based on discussion ID, round number, and message content hash
        # This ensures we only re-summarize if new messages were added to this round
        messages_hash = hashlib.md5(
            json.dumps(round_messages, sort_keys=True).encode()
        ).hexdigest()[:8]
        cache_key = f"round_summary:{discussion.id}:{round_num}:{messages_hash}"

        # Try to get from cache first
        cached_summary = await self.cache.get(cache_key)
        if cached_summary:
            logger.info(f"Using cached summary for round {round_num + 1}")
            return cached_summary

        # Build conversation text for this round
        conversation_parts = []
        phase_translations = {
            'opening': 'Opening',
            'development': 'Development',
            'debate': 'Debate',
            'closing': 'Closing'
        }

        for phase_name in ['opening', 'development', 'debate', 'closing']:
            if phase_name in round_messages:
                conversation_parts.append(f"\n[{phase_translations.get(phase_name, phase_name)} Phase]")
                for msg in round_messages[phase_name]:
                    conversation_parts.append(f"{msg['name']}: {msg['content']}")

        conversation_text = "\n".join(conversation_parts)

        # Build summarization prompt
        summary_prompt = f"""Please summarize the following discussion round (Round {round_num + 1}) in Chinese.
Focus on:
1. Key arguments presented by each participant
2. Main points of agreement and disagreement
3. Important conclusions reached

Keep the summary under 500 words. Preserve the names of participants.

Discussion to summarize:
{conversation_text}

Summary:"""

        try:
            logger.info(f"Generating summary for round {round_num + 1} using LLM")
            # Generate summary using LLM
            response = await self.llm_orchestrator.generate(
                provider_name,
                summary_prompt,
                max_tokens=800,
                temperature=0.5
            )

            if isinstance(response, dict):
                summary = response.get("content", "").strip()
            else:
                summary = str(response).strip()

            if not summary:
                summary = "Summary not available"

            # Cache the summary for 1 hour
            await self.cache.set(cache_key, summary, ttl=3600)
            logger.info(f"Cached summary for round {round_num + 1}")

            return summary

        except Exception as e:
            logger.error(f"Error summarizing round {round_num}: {e}")
            # Fallback: return truncated first few messages
            fallback_summary = conversation_text[:1000] + "..." if len(conversation_text) > 1000 else conversation_text
            return f"[Round {round_num + 1} discussion excerpt]\n{fallback_summary}"

    async def _generate_message(
        self,
        db: AsyncSession,
        discussion: Discussion,
        participant: DiscussionParticipant,
        character: Character,
        topic: Topic,
        provider_name: str
    ) -> DiscussionMessage:
        """Generate a message from a participant using streaming"""

        # Get messages organized by rounds for context
        # Show current round fully, and last 2 rounds briefly
        context_rounds = max(0, discussion.current_round - 2)
        messages_result = await db.execute(
            select(DiscussionMessage)
            .where(
                and_(
                    DiscussionMessage.discussion_id == discussion.id,
                    DiscussionMessage.round >= context_rounds,
                    DiscussionMessage.round <= discussion.current_round
                )
            )
            .order_by(DiscussionMessage.created_at.asc())
        )
        all_messages = list(messages_result.scalars().all())

        # Group messages by round and phase
        from collections import defaultdict
        rounds_messages = defaultdict(lambda: defaultdict(list))
        participant_names = {}  # Cache participant names

        for msg in all_messages:
            if msg.is_injected_question:
                rounds_messages[msg.round][msg.phase].append({
                    'name': 'User',
                    'content': msg.content
                })
            else:
                # Get character name
                if msg.participant_id not in participant_names:
                    participant_result = await db.execute(
                        select(DiscussionParticipant, Character)
                        .join(Character, DiscussionParticipant.character_id == Character.id)
                        .where(DiscussionParticipant.id == msg.participant_id)
                    )
                    pt_data = participant_result.first()
                    if pt_data:
                        _, msg_character = pt_data
                        participant_names[msg.participant_id] = msg_character.name
                    else:
                        participant_names[msg.participant_id] = 'Unknown'

                rounds_messages[msg.round][msg.phase].append({
                    'name': participant_names[msg.participant_id],
                    'content': msg.content
                })

        # Build context
        context_parts = [
            f"You are {character.name}.",
            f"Topic: {topic.title}",
            f"Description: {topic.description}",
            f"Current Round: {discussion.current_round + 1}/{discussion.max_rounds}",
            f"Current Phase: {discussion.current_phase}",
        ]

        # Add character configuration
        if character.config:
            if character.config.get("stance"):
                context_parts.append(f"Your Stance: {character.config['stance']}")
            if character.config.get("personality"):
                context_parts.append(f"Your Personality: {character.config['personality']}")
            if character.config.get("expression_style"):
                context_parts.append(f"Expression Style: {character.config['expression_style']}")

        # Add phase instruction
        phase_instruction = self.PHASES.get(discussion.current_phase, "")
        if phase_instruction:
            context_parts.append(f"Phase Instruction: {phase_instruction}")

        # Add conversation history organized by rounds and phases
        if rounds_messages:
            context_parts.append("\n=== Conversation History ===")

            for round_num in sorted(rounds_messages.keys()):
                if round_num == discussion.current_round:
                    # Current round: show full messages
                    context_parts.append(f"\n--- Current Round (Round {round_num + 1}) ---")
                    round_data = rounds_messages[round_num]
                    for phase_name in ['opening', 'development', 'debate', 'closing']:
                        if phase_name in round_data:
                            phase_translations = {
                                'opening': 'Opening',
                                'development': 'Development',
                                'debate': 'Debate',
                                'closing': 'Closing'
                            }
                            context_parts.append(f"\n[{phase_translations.get(phase_name, phase_name)} Phase]")
                            for msg in round_data[phase_name]:
                                context_parts.append(f"{msg['name']}: {msg['content']}")

                elif round_num >= discussion.current_round - 2:
                    # Recent rounds (within last 2 rounds): show full messages
                    context_parts.append(f"\n--- Round {round_num + 1} (Previous) ---")
                    round_data = rounds_messages[round_num]
                    for phase_name in ['opening', 'development', 'debate', 'closing']:
                        if phase_name in round_data:
                            phase_translations = {
                                'opening': 'Opening',
                                'development': 'Development',
                                'debate': 'Debate',
                                'closing': 'Closing'
                            }
                            context_parts.append(f"\n[{phase_translations.get(phase_name, phase_name)} Phase]")
                            for msg in round_data[phase_name]:
                                context_parts.append(f"{msg['name']}: {msg['content']}")

                else:
                    # Earlier rounds: use LLM summary
                    context_parts.append(f"\n--- Round {round_num + 1} Summary ---")
                    round_summary = await self._summarize_round_messages(
                        db, discussion, rounds_messages[round_num], round_num, provider_name
                    )
                    context_parts.append(round_summary)

        # Build prompt
        prompt = "\n".join(context_parts) + f"\n\n{character.name}, please respond:"

        # Create message with empty content first
        message = DiscussionMessage(
            discussion_id=discussion.id,
            participant_id=participant.id,
            round=discussion.current_round,
            phase=discussion.current_phase,
            content="",
            token_count=0,
            is_injected_question=False
        )
        db.add(message)
        await db.commit()  # Commit to get the message ID

        # Generate response using LLM with streaming
        content = ""
        tokens = 0
        chunk_count = 0
        try:
            # Stream the response
            logger.info(f"Starting stream generation for {character.name} in round {discussion.current_round}")

            async for chunk in self.llm_orchestrator.generate_stream(
                provider_name,
                prompt,
                max_tokens=500,
                temperature=0.8
            ):
                if chunk.get('is_complete'):
                    logger.info(f"Stream complete for {character.name}, finish_reason: {chunk.get('finish_reason')}")
                    break

                chunk_content = chunk.get('content', '')
                if chunk_content:
                    content += chunk_content
                    chunk_count += 1

                    # Update message content in database every few chunks
                    # This allows the frontend to see the progress
                    if chunk_count % 3 == 0:  # Update every 3 chunks to reduce DB calls
                        message.content = content
                        await db.commit()
                        logger.debug(f"Updated message {message.id} with {len(content)} characters")

            # Final update with complete content
            message.content = content
            logger.info(f"Streaming completed for {character.name}: {len(content)} characters, {chunk_count} chunks")

        except Exception as e:
            logger.error(f"LLM streaming error: {e}", exc_info=True)
            # Fallback message
            content = f"I'm {character.name}, and I believe {topic.title} is an important topic that needs careful consideration."
            message.content = content

        # Final update
        message.token_count = tokens
        discussion.total_tokens_used += tokens

        await db.commit()
        await self._cache_discussion_state(discussion)

        return message

    async def _advance_discussion(self, db: AsyncSession, discussion: Discussion):
        """Advance discussion to next phase/round"""
        phases = list(self.PHASES.keys())
        current_index = phases.index(discussion.current_phase)

        # Move to next phase
        if current_index < len(phases) - 1:
            discussion.current_phase = phases[current_index + 1]
        else:
            # All phases done, move to next round
            discussion.current_phase = phases[0]
            discussion.current_round += 1

        await db.commit()
        await self._cache_discussion_state(discussion)
