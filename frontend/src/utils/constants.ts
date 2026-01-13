/**
 * Application Constants
 */

/**
 * Discussion modes with descriptions
 */
export const DISCUSSION_MODES = {
  free: {
    label: 'Free Discussion',
    description: 'Characters freely express their perspectives'
  },
  structured: {
    label: 'Structured Debate',
    description: 'Formal debate with pro/con positions'
  },
  creative: {
    label: 'Creative Brainstorm',
    description: '"Yes, and" approach for creative ideas'
  },
  consensus: {
    label: 'Consensus Building',
    description: 'Find common ground and agreement'
  }
} as const

/**
 * Discussion phases with descriptions
 */
export const DISCUSSION_PHASES = {
  opening: {
    label: 'Opening',
    description: 'Introduction and initial positions'
  },
  development: {
    label: 'Development',
    description: 'Deep exploration of perspectives'
  },
  debate: {
    label: 'Debate',
    description: 'Active discussion and debate'
  },
  closing: {
    label: 'Closing',
    description: 'Summary and conclusions'
  }
} as const

/**
 * Character personality ranges
 */
export const PERSONALITY_RANGES = {
  openness: { min: 1, max: 10, label: 'Openness' },
  rigor: { min: 1, max: 10, label: 'Rigor' },
  critical_thinking: { min: 1, max: 10, label: 'Critical Thinking' },
  optimism: { min: 1, max: 10, label: 'Optimism' }
} as const

/**
 * Character expression styles
 */
export const EXPRESSION_STYLES = {
  formal: {
    label: 'Formal',
    description: 'Professional and structured language'
  },
  casual: {
    label: 'Casual',
    description: 'Relaxed and conversational tone'
  },
  technical: {
    label: 'Technical',
    description: 'Expert terminology and precision'
  },
  storytelling: {
    label: 'Storytelling',
    description: 'Narratives and anecdotes'
  }
} as const

/**
 * Character behavior patterns
 */
export const BEHAVIOR_PATTERNS = {
  active: {
    label: 'Active',
    description: 'Takes initiative and leads discussions'
  },
  passive: {
    label: 'Passive',
    description: 'Responds when prompted'
  },
  balanced: {
    label: 'Balanced',
    description: 'Middle-ground participation'
  }
} as const

/**
 * LLM providers
 */
export const LLM_PROVIDERS = {
  openai: {
    label: 'OpenAI',
    description: 'GPT models',
    models: ['gpt-4', 'gpt-4-turbo-preview', 'gpt-3.5-turbo']
  },
  anthropic: {
    label: 'Anthropic',
    description: 'Claude models',
    models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
  },
  custom: {
    label: 'Custom',
    description: 'OpenAI-compatible API',
    models: []
  }
} as const

/**
 * Pagination defaults
 */
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZES: [10, 20, 50, 100]
} as const

/**
 * Character limits
 */
export const LIMITS = {
  TOPIC_TITLE_MIN: 5,
  TOPIC_TITLE_MAX: 200,
  TOPIC_DESCRIPTION_MAX: 2000,
  TOPIC_CONTEXT_MAX: 5000,
  CHARACTER_NAME_MIN: 2,
  CHARACTER_NAME_MAX: 50,
  INJECTED_QUESTION_MAX: 500
} as const
