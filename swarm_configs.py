"""
EROS Configuration Template
Customize this file for your specific swarm use case
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SwarmConfig:
    """
    Main configuration for your EROS swarm
    """
    
    # PROJECT IDENTITY
    project_id: str = "MY-PROJECT-2025"
    project_description: str = "Description of what this swarm will build"
    
    # GLOBAL CONSTRAINTS (The Project DNA)
    # These are enforced across ALL agents via the Belief Registry
    global_constraints: Dict = None
    
    # TEAM STRUCTURE
    # Define how many managers and what they specialize in
    teams: List[Dict] = None
    
    # MONITORING CONFIGURATION
    monitoring_interval_seconds: float = 2.0  # How often managers check interns
    max_interns_per_manager: int = 10  # Max agents per manager
    
    # PAD TELEMETRY THRESHOLDS
    # Adjust these to tune failure detection sensitivity
    pad_pleasure_min: float = 0.2  # Min goal alignment (0.0-1.0)
    pad_arousal_max: float = 0.8   # Max stalling tolerance (0.0-1.0)
    pad_dominance_min: float = 0.3 # Min certainty required (0.0-1.0)
    
    # INTERVENTION POLICY
    auto_respawn_on_failure: bool = True
    max_respawn_attempts: int = 3
    
    # KIMI API CONFIGURATION (if using real API)
    kimi_api_key: Optional[str] = None
    kimi_model: str = "moonshot-v1-128k"
    kimi_temperature: float = 0.7
    kimi_max_tokens: int = 4096
    
    def __post_init__(self):
        # Set defaults if not provided
        if self.global_constraints is None:
            self.global_constraints = self._default_constraints()
        
        if self.teams is None:
            self.teams = self._default_teams()
    
    def _default_constraints(self) -> Dict:
        """Default project constraints - CUSTOMIZE THIS"""
        return {
            # Code Quality
            "coding_standard": "PEP8",
            "documentation_required": True,
            "test_coverage_min": 80,
            
            # Technology Stack
            "backend_language": "Python",
            "frontend_framework": "React",
            "database": "PostgreSQL",
            
            # Style Guide
            "ui_theme": "modern_minimal",
            "color_scheme": "blue_gray",
        }
    
    def _default_teams(self) -> List[Dict]:
        """Default team structure - CUSTOMIZE THIS"""
        return [
            {
                "name": "Backend Team",
                "manager_id": "backend_mgr",
                "specialties": ["api_developer", "auth_specialist", "database_specialist"],
                "max_agents": 10
            },
            {
                "name": "Frontend Team", 
                "manager_id": "frontend_mgr",
                "specialties": ["component_developer", "page_developer", "ui_specialist"],
                "max_agents": 8
            },
            {
                "name": "QA Team",
                "manager_id": "qa_mgr", 
                "specialties": ["test_engineer", "security_auditor", "performance_tester"],
                "max_agents": 5
            }
        ]


# ============================================================================
# EXAMPLE CONFIGURATIONS FOR COMMON USE CASES
# ============================================================================

# Example 1: CODE GENERATION SWARM
CODE_GEN_CONFIG = SwarmConfig(
    project_id="CODE-GEN-2025",
    project_description="Automated codebase generation with tests",
    global_constraints={
        "language": "Python 3.11",
        "coding_style": "PEP8 + Black",
        "type_hints": "required",
        "docstrings": "Google style",
        "test_framework": "pytest",
        "min_coverage": 85,
        "async_preferred": True,
        "error_handling": "comprehensive"
    },
    teams=[
        {
            "name": "Core Development",
            "manager_id": "core_mgr",
            "specialties": ["api_developer", "class_designer", "algorithm_specialist"],
            "max_agents": 12
        },
        {
            "name": "Testing & QA",
            "manager_id": "test_mgr",
            "specialties": ["unit_tester", "integration_tester", "fixture_creator"],
            "max_agents": 8
        },
        {
            "name": "Documentation",
            "manager_id": "doc_mgr",
            "specialties": ["docstring_writer", "readme_creator", "example_builder"],
            "max_agents": 5
        }
    ],
    monitoring_interval_seconds=1.5,  # Faster monitoring for code tasks
    pad_pleasure_min=0.3,  # Stricter alignment needed
)


# Example 2: CONTENT CREATION SWARM
CONTENT_SWARM_CONFIG = SwarmConfig(
    project_id="CONTENT-2025",
    project_description="Multi-channel content creation and optimization",
    global_constraints={
        "brand_voice": "professional_friendly",
        "tone": "conversational",
        "target_audience": "B2B SaaS decision-makers",
        "seo_optimized": True,
        "max_reading_level": "grade_10",
        "citation_required": True,
        "fact_check": "required",
        "content_format": "markdown"
    },
    teams=[
        {
            "name": "Research Team",
            "manager_id": "research_mgr",
            "specialties": ["topic_researcher", "competitor_analyst", "trend_analyst"],
            "max_agents": 6
        },
        {
            "name": "Writing Team",
            "manager_id": "writing_mgr",
            "specialties": ["blog_writer", "case_study_writer", "whitepaper_writer"],
            "max_agents": 10
        },
        {
            "name": "SEO & Optimization",
            "manager_id": "seo_mgr",
            "specialties": ["keyword_optimizer", "meta_writer", "readability_editor"],
            "max_agents": 5
        }
    ],
    monitoring_interval_seconds=3.0,  # Slower ok for content
    pad_pleasure_min=0.25,  # Allow more creativity
    pad_dominance_min=0.2,  # Writing can be exploratory
)


# Example 3: E-COMMERCE PLATFORM SWARM
ECOMMERCE_CONFIG = SwarmConfig(
    project_id="ECOMMERCE-PLATFORM",
    project_description="Full-stack e-commerce platform with payment integration",
    global_constraints={
        # Design System
        "primary_color": "#2563EB",
        "secondary_color": "#10B981",
        "font_family": "Inter, sans-serif",
        "spacing_unit": "8px",
        "border_radius": "8px",
        
        # Technical
        "backend_framework": "FastAPI",
        "frontend_framework": "Next.js 14",
        "database": "PostgreSQL 15",
        "cache": "Redis",
        "api_version": "v2",
        "api_docs": "OpenAPI 3.0",
        
        # Security & Compliance
        "auth_method": "JWT + OAuth2",
        "encryption": "AES-256",
        "pci_dss_compliant": True,
        "gdpr_compliant": True,
        "rate_limiting": "required",
        "input_validation": "strict",
        
        # Performance
        "response_time_max": "200ms",
        "lighthouse_score_min": 90,
        "cache_strategy": "aggressive",
    },
    teams=[
        {
            "name": "Backend API",
            "manager_id": "backend_mgr",
            "specialties": [
                "auth_specialist", "payment_specialist", "api_developer",
                "search_specialist", "notification_specialist"
            ],
            "max_agents": 10
        },
        {
            "name": "Frontend UI",
            "manager_id": "frontend_mgr",
            "specialties": [
                "component_developer", "page_developer", "checkout_specialist",
                "admin_specialist", "mobile_specialist"
            ],
            "max_agents": 8
        },
        {
            "name": "Database & Cache",
            "manager_id": "data_mgr",
            "specialties": [
                "schema_architect", "migration_specialist", "cache_specialist",
                "performance_specialist", "backup_specialist"
            ],
            "max_agents": 5
        },
        {
            "name": "DevOps & Infrastructure",
            "manager_id": "devops_mgr",
            "specialties": [
                "container_specialist", "k8s_specialist", "cicd_specialist",
                "monitoring_specialist", "security_specialist"
            ],
            "max_agents": 6
        },
        {
            "name": "QA & Testing",
            "manager_id": "qa_mgr",
            "specialties": [
                "test_engineer", "security_auditor", "e2e_specialist",
                "performance_tester", "accessibility_specialist"
            ],
            "max_agents": 6
        }
    ],
    monitoring_interval_seconds=2.0,
    pad_pleasure_min=0.3,
    pad_arousal_max=0.7,  # Stricter for production code
    pad_dominance_min=0.4,  # Need high certainty
)


# Example 4: RESEARCH & ANALYSIS SWARM
RESEARCH_CONFIG = SwarmConfig(
    project_id="RESEARCH-2025",
    project_description="Deep research and competitive analysis",
    global_constraints={
        "citation_format": "APA 7th",
        "sources_required": True,
        "min_sources_per_claim": 2,
        "source_quality": "peer_reviewed_preferred",
        "fact_check": "required",
        "bias_check": "required",
        "recency_required": "within_12_months",
        "output_format": "markdown_with_citations",
        "evidence_level": "comprehensive"
    },
    teams=[
        {
            "name": "Data Collection",
            "manager_id": "collection_mgr",
            "specialties": [
                "academic_researcher", "industry_researcher", "patent_researcher",
                "news_analyst", "social_analyst"
            ],
            "max_agents": 10
        },
        {
            "name": "Analysis",
            "manager_id": "analysis_mgr",
            "specialties": [
                "data_analyst", "trend_analyst", "competitive_analyst",
                "synthesis_specialist", "pattern_detector"
            ],
            "max_agents": 8
        },
        {
            "name": "Quality Assurance",
            "manager_id": "qa_mgr",
            "specialties": [
                "fact_checker", "bias_detector", "citation_validator",
                "logic_checker", "peer_reviewer"
            ],
            "max_agents": 5
        }
    ],
    monitoring_interval_seconds=3.0,  # Research takes time
    pad_pleasure_min=0.2,  # Allow exploration
    pad_arousal_max=0.9,  # Research can iterate
    pad_dominance_min=0.25,  # Uncertainty ok in research
)


# Example 5: RAPID PROTOTYPING SWARM
PROTOTYPE_CONFIG = SwarmConfig(
    project_id="PROTOTYPE-2025",
    project_description="Fast MVP development for user testing",
    global_constraints={
        "speed_priority": "high",
        "quality_threshold": "MVP_acceptable",
        "tech_stack": "fastest_to_market",
        "framework": "Next.js + Supabase",
        "styling": "Tailwind + shadcn/ui",
        "auth": "Supabase Auth",
        "deployment": "Vercel",
        "analytics": "Vercel Analytics",
        "testing": "critical_paths_only",
        "documentation": "minimal_viable"
    },
    teams=[
        {
            "name": "Full-Stack Dev",
            "manager_id": "fullstack_mgr",
            "specialties": [
                "rapid_developer", "integration_specialist", "ui_builder"
            ],
            "max_agents": 8
        },
        {
            "name": "Critical Testing",
            "manager_id": "test_mgr",
            "specialties": ["smoke_tester", "user_flow_tester"],
            "max_agents": 3
        }
    ],
    monitoring_interval_seconds=1.0,  # Fast feedback for rapid dev
    pad_pleasure_min=0.15,  # Lower bar for MVP
    pad_arousal_max=0.85,  # Tolerate more iteration
)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    print("EROS Configuration Templates\n")
    print("=" * 80)
    
    configs = {
        "Code Generation": CODE_GEN_CONFIG,
        "Content Creation": CONTENT_SWARM_CONFIG,
        "E-Commerce Platform": ECOMMERCE_CONFIG,
        "Research & Analysis": RESEARCH_CONFIG,
        "Rapid Prototyping": PROTOTYPE_CONFIG,
    }
    
    for name, config in configs.items():
        print(f"\n{name}:")
        print(f"  Project ID: {config.project_id}")
        print(f"  Description: {config.project_description}")
        print(f"  Teams: {len(config.teams)}")
        print(f"  Global Constraints: {len(config.global_constraints)} items")
        print(f"  Monitoring Interval: {config.monitoring_interval_seconds}s")
    
    print("\n" + "=" * 80)
    print("\nTo use a config:")
    print("  from swarm_configs import ECOMMERCE_CONFIG")
    print("  orchestrator = SovereignOrchestrator(")
    print("      project_id=ECOMMERCE_CONFIG.project_id,")
    print("      global_constraints=ECOMMERCE_CONFIG.global_constraints")
    print("  )")
