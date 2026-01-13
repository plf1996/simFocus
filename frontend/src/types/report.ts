/**
 * Report data types for frontend
 */

import type { DiscussionPhase } from '../../../shared/types'

/**
 * Report model
 */
export interface Report {
  id: string
  discussion_id: string
  overview: ReportOverview
  viewpoints_summary: ViewpointSummary[]
  consensus: Consensus
  controversies: Controversy[]
  insights: Insight[]
  recommendations: Recommendation[]
  quality_scores: QualityScores
  generation_time_ms: number
  created_at: string
}

export interface ReportOverview {
  topic: string
  participant_count: number
  duration_seconds: number
  round_count: number
  total_tokens: number
}

export interface ViewpointSummary {
  character_name: string
  character_stance: string
  main_arguments: string[]
  position_changes?: PositionChange[]
}

export interface PositionChange {
  from_phase: DiscussionPhase
  to_phase: DiscussionPhase
  old_position: string
  new_position: string
}

export interface Consensus {
  points: string[]
  supporting_arguments: Record<string, string[]>
}

export interface Controversy {
  topic: string
  disagreement_summary: string
  opposing_views: {
    character_name: string
    position: string
    arguments: string[]
  }[]
  resolution_status: 'unresolved' | 'partial' | 'resolved'
}

export interface Insight {
  category: string
  insight: string
  evidence: string[]
}

export interface Recommendation {
  priority: 'high' | 'medium' | 'low'
  recommendation: string
  rationale: string
}

export interface QualityScores {
  depth: number
  diversity: number
  constructive: number
  coherence: number
  overall: number
}

/**
 * Report export format
 */
export type ReportExportFormat = 'pdf' | 'markdown' | 'json'
