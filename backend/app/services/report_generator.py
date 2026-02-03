from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from app.models.report import Report
from app.models.discussion import Discussion
from app.models.message import DiscussionMessage
from app.models.participant import DiscussionParticipant
from app.models.character import Character
from app.models.topic import Topic
from app.services.llm_orchestrator import LLMOrchestrator
import json


class ReportGeneratorService:
    """Service for generating discussion reports"""

    def __init__(self, db: AsyncSession, llm_orchestrator: LLMOrchestrator):
        self.db = db
        self.llm_orchestrator = llm_orchestrator

    async def generate_report(self, discussion_id: UUID) -> Report:
        """Generate a comprehensive report for a completed discussion"""
        # Get discussion
        discussion_result = await self.db.execute(
            select(Discussion).where(Discussion.id == discussion_id)
        )
        discussion = discussion_result.scalar_one_or_none()
        if not discussion:
            raise ValueError("Discussion not found")

        if discussion.status != "completed":
            raise ValueError("Discussion must be completed to generate report")

        # Get topic
        topic_result = await self.db.execute(
            select(Topic).where(Topic.id == discussion.topic_id)
        )
        topic = topic_result.scalar_one_or_none()

        # Get participants and characters
        participants_result = await self.db.execute(
            select(DiscussionParticipant, Character)
            .join(Character, DiscussionParticipant.character_id == Character.id)
            .where(DiscussionParticipant.discussion_id == discussion_id)
        )
        participants_data = [
            {
                "participant": p,
                "character": c
            }
            for p, c in participants_result.all()
        ]

        # Get all messages
        messages_result = await self.db.execute(
            select(DiscussionMessage)
            .where(DiscussionMessage.discussion_id == discussion_id)
            .order_by(DiscussionMessage.created_at)
        )
        messages = list(messages_result.scalars().all())

        # Get LLM provider for summarization
        provider_name = discussion.llm_provider or "default"

        # Generate report sections with LLM
        overview = await self._generate_overview(discussion, topic, messages)
        summary = await self._generate_summary_with_llm(discussion, topic, participants_data, messages, provider_name)
        viewpoints_summary = await self._generate_viewpoints_summary(participants_data, messages)
        consensus = await self._generate_consensus_with_llm(participants_data, messages, topic, provider_name)
        controversies = await self._generate_controversies_with_llm(participants_data, messages, topic, provider_name)
        insights = await self._generate_insights_with_llm(messages, discussion, topic, provider_name)
        recommendations = await self._generate_recommendations_with_llm(participants_data, messages, topic, provider_name)
        quality_scores = await self._calculate_quality_scores(messages, participants_data)

        # Build full transcript
        transcript = self._build_transcript(participants_data, messages)

        # Check if report already exists
        existing_report = await self.db.execute(
            select(Report).where(Report.discussion_id == discussion_id)
        )
        existing = existing_report.scalar_one_or_none()

        if existing:
            # Update existing report
            existing.overview = overview
            existing.summary = summary
            existing.viewpoints_summary = viewpoints_summary
            existing.consensus = consensus
            existing.controversies = controversies
            existing.insights = insights
            existing.recommendations = recommendations
            existing.quality_scores = quality_scores
            existing.transcript = transcript
            existing.updated_at = datetime.utcnow()
            report = existing
        else:
            # Create new report
            report = Report(
                discussion_id=discussion_id,
                overview=overview,
                summary=summary,
                viewpoints_summary=viewpoints_summary,
                consensus=consensus,
                controversies=controversies,
                insights=insights,
                recommendations=recommendations,
                quality_scores=quality_scores,
                transcript=transcript
            )
            self.db.add(report)

        await self.db.commit()
        await self.db.refresh(report)

        return report

    async def get_report_by_discussion_id(self, discussion_id: UUID) -> Optional[Report]:
        """Get report for a discussion"""
        result = await self.db.execute(
            select(Report).where(Report.discussion_id == discussion_id)
        )
        return result.scalar_one_or_none()

    async def _generate_overview(
        self,
        discussion: Discussion,
        topic: Topic,
        messages: List[DiscussionMessage]
    ) -> Dict[str, Any]:
        """Generate report overview section"""
        if not topic:
            return {}

        duration = 0
        if discussion.started_at and discussion.completed_at:
            duration = int((discussion.completed_at - discussion.started_at).total_seconds())

        # Calculate actual token usage from messages
        actual_tokens = sum(m.token_count for m in messages if m.token_count)

        return {
            "topic_title": topic.title,
            "topic_description": topic.description,
            "topic_context": topic.context,
            "discussion_duration_seconds": duration,
            "total_rounds": discussion.current_round + 1,  # Convert 0-based to 1-based
            "total_messages": len(messages),
            "participant_count": len([m for m in messages if not m.is_injected_question]),
            "llm_provider": discussion.llm_provider,
            "llm_model": discussion.llm_model,
            "total_tokens_used": actual_tokens if actual_tokens > 0 else discussion.total_tokens_used,
            "estimated_cost_usd": float(discussion.estimated_cost_usd) if discussion.estimated_cost_usd else 0.0
        }

    async def _generate_summary_with_llm(
        self,
        discussion: Discussion,
        topic: Topic,
        participants_data: List[Dict[str, Any]],
        messages: List[DiscussionMessage],
        provider_name: str
    ) -> str:
        """Generate comprehensive summary using LLM"""
        if not topic:
            return ""

        # Build participant list
        participant_list = "\n".join([
            f"- {data['character'].name}: {data['character'].config.get('profession', 'N/A')}"
            for data in participants_data
        ])

        # Build conversation summary (last 10 messages for context)
        conversation_snippet = "\n".join([
            f"{m.participant_id if not m.is_injected_question else 'User'}: {m.content[:200]}..."
            for m in messages[-10:] if len(m.content) > 0
        ])

        prompt = f"""请为以下讨论生成一份全面的总结报告。

## 讨论主题
**标题**: {topic.title}
**描述**: {topic.description}

## 参与者
{participant_list}

## 讨论概况
- 总轮次: {discussion.current_round + 1}
- 总消息数: {len(messages)}
- 讨论时长: {discussion.started_at and discussion.completed_at}

## 最近对话片段
{conversation_snippet}

请生成一份包含以下内容的总结报告（使用Markdown格式）：

### 1. 核心观点总结
概括3-5个关键论点和主要讨论内容

### 2. 立场分析
分析各参与者的核心立场和主要论据

### 3. 主要共识
列出参与者达成一致的观点

### 4. 争议焦点
指出主要的分歧和辩论点

### 5. 关键洞察
提炼讨论中的有价值见解

### 6. 行动建议
提供基于讨论的可行建议

请确保总结条理清晰、语言简练，重点突出核心价值。
"""

        try:
            response = await self.llm_orchestrator.generate(
                provider_name,
                prompt,
                max_tokens=2000,
                temperature=0.5
            )

            if isinstance(response, dict):
                return response.get("content", "无法生成总结")
            else:
                return str(response)

        except Exception as e:
            # Fallback to simple summary
            return f"## 讨论总结\n\n关于**{topic.title}**的讨论已完成，共有{discussion.current_round + 1}轮、{len(messages)}条消息。"

    async def _generate_consensus_with_llm(
        self,
        participants_data: List[Dict[str, Any]],
        messages: List[DiscussionMessage],
        topic: Topic,
        provider_name: str
    ) -> Dict[str, Any]:
        """Identify consensus points using LLM"""
        if not topic or not messages:
            return {"agreements": [], "joint_recommendations": [], "supporting_arguments": []}

        # Build conversation text for analysis
        conversation_text = "\n".join([
            f"消息{ i + 1}: {m.content[:300]}..."
            for i, m in enumerate(messages[:20])  # Limit to prevent token overflow
        ])

        prompt = f"""分析以下关于"{topic.title}"的讨论，总结参与者的共识点。

讨论内容：
{conversation_text}

请提供：
1. 主要共识点（3-5个）
2. 共同建议（如果有）
3. 支持共识的关键论据

以JSON格式返回：
{{
    "agreements": ["共识点1", "共识点2"],
    "joint_recommendations": ["建议1", "建议2"],
    "supporting_arguments": ["论据1", "论据2"]
}}
"""

        try:
            response = await self.llm_orchestrator.generate(
                provider_name,
                prompt,
                max_tokens=1000,
                temperature=0.3
            )

            if isinstance(response, dict):
                content = response.get("content", "")
            else:
                content = str(response)

            # Try to parse JSON
            import json
            try:
                # Extract JSON from response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
            except:
                pass

        except Exception as e:
            pass

        return {"agreements": [], "joint_recommendations": [], "supporting_arguments": []}

    async def _generate_controversies_with_llm(
        self,
        participants_data: List[Dict[str, Any]],
        messages: List[DiscussionMessage],
        topic: Topic,
        provider_name: str
    ) -> List[Dict[str, Any]]:
        """Identify controversy points using LLM"""
        if not topic or not messages:
            return []

        # Get participant messages grouped by character
        from collections import defaultdict
        character_messages = defaultdict(list)
        for m in messages:
            if not m.is_injected_question:
                character_messages[m.participant_id].append(m.content[:200])

        prompt = f"""分析以下关于"{topic.title}"的讨论，找出主要的争议和分歧点。

讨论片段：
{dict(list(character_messages.items())[:3])}

请列出3-5个主要的争议点，每个包括：
- 争议主题
- 对立观点
- 涉及的参与者

以JSON数组格式返回。
"""

        try:
            response = await self.llm_orchestrator.generate(
                provider_name,
                prompt,
                max_tokens=1000,
                temperature=0.3
            )

            if isinstance(response, dict):
                content = response.get("content", "")
            else:
                content = str(response)

            # Try to parse JSON array
            import json
            try:
                start_idx = content.find('[')
                end_idx = content.rfind(']') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
            except:
                pass

        except Exception as e:
            pass

        return []

    async def _generate_insights_with_llm(
        self,
        messages: List[DiscussionMessage],
        discussion: Discussion,
        topic: Topic,
        provider_name: str
    ) -> List[Dict[str, Any]]:
        """Generate insights using LLM"""
        return []

    async def _generate_recommendations_with_llm(
        self,
        participants_data: List[Dict[str, Any]],
        messages: List[DiscussionMessage],
        topic: Topic,
        provider_name: str
    ) -> List[Dict[str, Any]]:
        """Generate recommendations using LLM"""
        return []

    def _build_transcript(
        self,
        participants_data: List[Dict[str, Any]],
        messages: List[DiscussionMessage]
    ) -> str:
        """Build full transcript in markdown format"""
        lines = []
        lines.append(f"# 讨论记录\n")

        # Create participant ID to name mapping
        participant_map = {}
        for data in participants_data:
            participant_map[data['participant'].id] = data['character'].name

        # Group messages by round and phase
        from collections import defaultdict
        rounds = defaultdict(lambda: defaultdict(list))
        for msg in messages:
            rounds[msg.round][msg.phase].append(msg)

        # Build transcript
        for round_num in sorted(rounds.keys()):
            lines.append(f"\n## 第 {round_num + 1} 轮\n")

            for phase_name in ['opening', 'development', 'debate', 'closing']:
                if phase_name in rounds[round_num]:
                    phase_translations = {
                        'opening': '开场阶段',
                        'development': '发展阶段',
                        'debate': '辩论阶段',
                        'closing': '总结阶段'
                    }
                    lines.append(f"\n### {phase_translations.get(phase_name, phase_name)}\n")

                    for msg in rounds[round_num][phase_name]:
                        if msg.is_injected_question:
                            lines.append(f"\n**用户提问**: {msg.content}\n")
                        else:
                            char_name = participant_map.get(msg.participant_id, '未知角色')
                            lines.append(f"\n#### {char_name}\n\n{msg.content}\n")

        return "\n".join(lines)

    async def _generate_viewpoints_summary(
        self,
        participants_data: List[Dict[str, Any]],
        messages: List[DiscussionMessage]
    ) -> List[Dict[str, Any]]:
        """Generate summary of each character's viewpoints"""
        viewpoints = []

        for data in participants_data:
            participant = data["participant"]
            character = data["character"]

            # Get messages from this participant
            character_messages = [
                m for m in messages
                if m.participant_id == participant.id
            ]

            # Extract key points from messages (simplified version)
            key_points = []
            for msg in character_messages:
                if len(msg.content) > 50:  # Filter out very short messages
                    # In production, use LLM to extract key points
                    key_points.append(msg.content[:200] + "..." if len(msg.content) > 200 else msg.content)

            viewpoints.append({
                "character_id": str(character.id),
                "character_name": character.name,
                "stance": participant.stance or character.config.get("stance", "neutral"),
                "message_count": participant.message_count,
                "total_tokens": participant.total_tokens,
                "key_points": key_points[:5]  # Limit to 5 key points
            })

        return viewpoints

    async def _generate_consensus(
        self,
        participants_data: List[Dict[str, Any]],
        messages: List[DiscussionMessage]
    ) -> Dict[str, Any]:
        """Identify consensus points from discussion"""
        # Simplified version - in production, use LLM for better analysis
        return {
            "agreements": [],
            "joint_recommendations": [],
            "supporting_arguments": []
        }

    async def _generate_controversies(
        self,
        participants_data: List[Dict[str, Any]],
        messages: List[DiscussionMessage]
    ) -> List[Dict[str, Any]]:
        """Identify controversy points from discussion"""
        # Simplified version - in production, use LLM to identify disagreements
        return []

    async def _generate_insights(
        self,
        messages: List[DiscussionMessage],
        discussion: Discussion
    ) -> List[Dict[str, Any]]:
        """Generate insights from the discussion"""
        # Simplified version - in production, use LLM
        return []

    async def _generate_recommendations(
        self,
        participants_data: List[Dict[str, Any]],
        messages: List[DiscussionMessage],
        topic: Topic
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        # Simplified version - in production, use LLM
        return []

    async def _calculate_quality_scores(
        self,
        messages: List[DiscussionMessage],
        participants_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate quality scores for the discussion"""
        total_messages = len(messages)
        total_participants = len(participants_data)

        if total_messages == 0 or total_participants == 0:
            return {
                "depth": 0.0,
                "diversity": 0.0,
                "constructive": 0.0,
                "coherence": 0.0,
                "overall": 0.0
            }

        # Depth: Average message length (proxy for depth)
        avg_length = sum(len(m.content) for m in messages) / total_messages
        depth_score = min(100, avg_length / 5)  # Normalize to 0-100

        # Diversity: How evenly distributed messages are among participants
        message_counts = [p["participant"].message_count for p in participants_data]
        max_count = max(message_counts)
        min_count = min(message_counts)
        if max_count == 0:
            diversity_score = 0.0
        else:
            diversity_score = (1 - (max_count - min_count) / max_count) * 100

        # Constructive: Ratio of non-empty messages
        non_empty_count = sum(1 for m in messages if len(m.content.strip()) > 20)
        constructive_score = (non_empty_count / total_messages) * 100

        # Coherence: Phase transitions (simplified)
        unique_phases = len(set(m.phase for m in messages))
        coherence_score = min(100, (unique_phases / 4) * 100)  # 4 phases total

        # Overall: Average of all scores
        overall_score = (depth_score + diversity_score + constructive_score + coherence_score) / 4

        return {
            "depth": round(depth_score, 2),
            "diversity": round(diversity_score, 2),
            "constructive": round(constructive_score, 2),
            "coherence": round(coherence_score, 2),
            "overall": round(overall_score, 2)
        }
