"""Template seeder service for populating initial templates.

Seeds the database with:
- Project templates (8+)
- Workflow templates (5+)
- Conversation examples (6+)

Run this after migrations to populate template data.
"""
from sqlalchemy import text
from app.database import async_session_factory


async def seed_project_templates():
    """Seed project templates into the database."""
    templates = [
        {
            "title": "Agile Sprint Planning",
            "description": "Organize a 2-week sprint with tasks, goals, and retrospective planning",
            "category": "development",
            "industry": "developers",
            "template_data": {"sprint_duration": "2 weeks", "methodology": "scrum"},
            "default_tasks": [
                "Define sprint goal",
                "Review backlog and prioritize stories",
                "Estimate story points",
                "Assign tasks to team members",
                "Set up daily standup schedule",
                "Plan sprint retrospective"
            ],
            "default_research_topics": [
                "Sprint planning best practices",
                "Story point estimation techniques",
                "Daily standup formats"
            ],
            "icon": "🎯",
            "color": "#6C5CE7",
            "tags": ["agile", "scrum", "development", "teamwork"],
            "is_featured": True
        },
        {
            "title": "Research Project",
            "description": "Comprehensive academic or professional research project with literature review and findings",
            "category": "education",
            "industry": "students",
            "template_data": {"research_type": "academic"},
            "default_tasks": [
                "Define research question",
                "Conduct literature review",
                "Design methodology",
                "Collect data",
                "Analyze findings",
                "Write conclusions"
            ],
            "default_research_topics": [
                "Research methodologies",
                "Literature review frameworks",
                "Data analysis techniques",
                "Academic writing guidelines"
            ],
            "icon": "🔬",
            "color": "#0984E3",
            "tags": ["research", "academic", "education", "analysis"],
            "is_featured": True
        },
        {
            "title": "Marketing Campaign",
            "description": "Plan and execute a multi-channel marketing campaign with metrics and optimization",
            "category": "business",
            "industry": "entrepreneurs",
            "template_data": {"campaign_type": "multi-channel"},
            "default_tasks": [
                "Define target audience",
                "Set campaign goals and KPIs",
                "Choose marketing channels",
                "Create content calendar",
                "Design creatives",
                "Launch and monitor",
                "Analyze results and optimize"
            ],
            "default_research_topics": [
                "Target audience personas",
                "Channel performance benchmarks",
                "Content marketing strategies",
                "A/B testing best practices"
            ],
            "icon": "📣",
            "color": "#FD79A8",
            "tags": ["marketing", "business", "campaign", "growth"],
            "is_featured": True
        },
        {
            "title": "Product Launch",
            "description": "Coordinate a successful product launch from planning to post-launch analysis",
            "category": "business",
            "industry": "entrepreneurs",
            "template_data": {"launch_type": "new_product"},
            "default_tasks": [
                "Create product positioning",
                "Develop go-to-market strategy",
                "Build pre-launch buzz",
                "Coordinate launch day activities",
                "Monitor customer feedback",
                "Post-launch optimization"
            ],
            "default_research_topics": [
                "Product launch frameworks",
                "GTM strategy templates",
                "Launch day checklists",
                "Early adopter engagement"
            ],
            "icon": "🚀",
            "color": "#00B894",
            "tags": ["product", "launch", "business", "strategy"],
            "is_featured": True
        },
        {
            "title": "Personal Goal Tracker",
            "description": "Track and achieve personal goals with milestones, habits, and progress monitoring",
            "category": "personal",
            "industry": "general",
            "template_data": {"goal_type": "personal_development"},
            "default_tasks": [
                "Define SMART goals",
                "Break down into milestones",
                "Create daily habits",
                "Track weekly progress",
                "Adjust strategy as needed",
                "Celebrate achievements"
            ],
            "default_research_topics": [
                "SMART goals framework",
                "Habit formation science",
                "Progress tracking methods"
            ],
            "icon": "⭐",
            "color": "#FDCB6E",
            "tags": ["goals", "personal", "habits", "self-improvement"],
            "is_featured": False
        },
        {
            "title": "Learning Path",
            "description": "Structured learning journey for mastering a new skill or subject area",
            "category": "education",
            "industry": "students",
            "template_data": {"learning_type": "skill_development"},
            "default_tasks": [
                "Assess current knowledge level",
                "Set learning objectives",
                "Curate learning resources",
                "Create study schedule",
                "Practice and apply knowledge",
                "Test understanding"
            ],
            "default_research_topics": [
                "Learning resources",
                "Practice projects",
                "Community and forums",
                "Assessment methods"
            ],
            "icon": "📚",
            "color": "#A29BFE",
            "tags": ["learning", "education", "skill", "development"],
            "is_featured": False
        },
        {
            "title": "Event Planning",
            "description": "Organize a successful event from venue selection to post-event follow-up",
            "category": "personal",
            "industry": "general",
            "template_data": {"event_type": "general"},
            "default_tasks": [
                "Define event goals and budget",
                "Choose venue and date",
                "Create guest list",
                "Plan agenda and activities",
                "Coordinate logistics",
                "Send invitations",
                "Day-of coordination",
                "Post-event follow-up"
            ],
            "default_research_topics": [
                "Event planning checklists",
                "Venue options",
                "Catering services",
                "Event timeline templates"
            ],
            "icon": "🎉",
            "color": "#FF7675",
            "tags": ["event", "planning", "organization", "coordination"],
            "is_featured": False
        },
        {
            "title": "Client Onboarding",
            "description": "Streamlined client onboarding process with welcome materials and setup tasks",
            "category": "business",
            "industry": "entrepreneurs",
            "template_data": {"onboarding_type": "client"},
            "default_tasks": [
                "Send welcome email",
                "Schedule kickoff call",
                "Gather client requirements",
                "Set expectations and timelines",
                "Provide access to tools",
                "Complete initial setup",
                "Schedule regular check-ins"
            ],
            "default_research_topics": [
                "Client onboarding best practices",
                "Welcome email templates",
                "Requirement gathering frameworks"
            ],
            "icon": "🤝",
            "color": "#74B9FF",
            "tags": ["client", "onboarding", "business", "service"],
            "is_featured": False
        }
    ]

    async with async_session_factory() as db:
        for tmpl in templates:
            await db.execute(
                text("""
                    INSERT INTO project_templates
                    (title, description, category, industry, template_data, default_tasks,
                     default_research_topics, icon, color, tags, is_featured)
                    VALUES (:title, :desc, :cat, :ind, :data, :tasks, :research, :icon, :color, :tags, :featured)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "title": tmpl["title"],
                    "desc": tmpl["description"],
                    "cat": tmpl["category"],
                    "ind": tmpl["industry"],
                    "data": tmpl["template_data"],
                    "tasks": tmpl["default_tasks"],
                    "research": tmpl["default_research_topics"],
                    "icon": tmpl["icon"],
                    "color": tmpl["color"],
                    "tags": tmpl["tags"],
                    "featured": tmpl["is_featured"]
                }
            )
        await db.commit()


async def seed_workflow_templates():
    """Seed workflow templates into the database."""
    workflows = [
        {
            "title": "Daily Standup",
            "description": "Quick daily check-in to align on priorities and blockers",
            "workflow_type": "standup",
            "steps": [
                {"step": 1, "title": "What did I accomplish yesterday?", "duration": 2},
                {"step": 2, "title": "What will I work on today?", "duration": 2},
                {"step": 3, "title": "Any blockers or challenges?", "duration": 1}
            ],
            "prompts": [
                "List 3 key accomplishments from yesterday",
                "What are my top 3 priorities for today?",
                "What's blocking my progress?"
            ],
            "expected_duration_minutes": 5,
            "icon": "☀️",
            "difficulty": "beginner",
            "tags": ["standup", "daily", "team", "agile"],
            "is_featured": True
        },
        {
            "title": "Weekly Review",
            "description": "Reflect on the week's progress, learnings, and plan for next week",
            "workflow_type": "review",
            "steps": [
                {"step": 1, "title": "Review completed tasks", "duration": 5},
                {"step": 2, "title": "Identify wins and challenges", "duration": 5},
                {"step": 3, "title": "Capture lessons learned", "duration": 5},
                {"step": 4, "title": "Plan next week's priorities", "duration": 5}
            ],
            "prompts": [
                "What went well this week?",
                "What could have gone better?",
                "What did I learn?",
                "What are my top priorities for next week?"
            ],
            "expected_duration_minutes": 20,
            "icon": "📊",
            "difficulty": "beginner",
            "tags": ["review", "weekly", "reflection", "planning"],
            "is_featured": True
        },
        {
            "title": "Brainstorming Session",
            "description": "Generate creative ideas without judgment, then refine the best ones",
            "workflow_type": "brainstorm",
            "steps": [
                {"step": 1, "title": "Define the problem or opportunity", "duration": 5},
                {"step": 2, "title": "Generate ideas rapidly (no filtering)", "duration": 15},
                {"step": 3, "title": "Group similar ideas", "duration": 5},
                {"step": 4, "title": "Evaluate and prioritize", "duration": 10}
            ],
            "prompts": [
                "What problem are we solving?",
                "What if there were no constraints?",
                "How might we approach this differently?",
                "Which ideas have the most potential?"
            ],
            "expected_duration_minutes": 35,
            "icon": "💡",
            "difficulty": "intermediate",
            "tags": ["brainstorm", "creativity", "ideation", "innovation"],
            "is_featured": True
        },
        {
            "title": "Monthly Planning",
            "description": "Set goals and priorities for the upcoming month aligned with long-term objectives",
            "workflow_type": "planning",
            "steps": [
                {"step": 1, "title": "Review previous month's progress", "duration": 10},
                {"step": 2, "title": "Define monthly goals (3-5 max)", "duration": 15},
                {"step": 3, "title": "Break goals into weekly milestones", "duration": 15},
                {"step": 4, "title": "Identify potential obstacles", "duration": 10},
                {"step": 5, "title": "Schedule time blocks for priorities", "duration": 10}
            ],
            "prompts": [
                "What are my top 3 goals for this month?",
                "What milestones will I hit each week?",
                "What might get in my way?",
                "How will I measure success?"
            ],
            "expected_duration_minutes": 60,
            "icon": "📅",
            "difficulty": "intermediate",
            "tags": ["planning", "monthly", "goals", "strategy"],
            "is_featured": False
        },
        {
            "title": "Sprint Retrospective",
            "description": "Team reflection on what worked, what didn't, and improvements for next sprint",
            "workflow_type": "retrospective",
            "steps": [
                {"step": 1, "title": "Set the stage and ground rules", "duration": 5},
                {"step": 2, "title": "Gather data (what happened)", "duration": 10},
                {"step": 3, "title": "Generate insights (why it happened)", "duration": 15},
                {"step": 4, "title": "Decide what to do (action items)", "duration": 10},
                {"step": 5, "title": "Close the retrospective", "duration": 5}
            ],
            "prompts": [
                "What went well during the sprint?",
                "What didn't go well?",
                "What puzzles or questions do we have?",
                "What will we try differently next sprint?"
            ],
            "expected_duration_minutes": 45,
            "icon": "🔄",
            "difficulty": "advanced",
            "tags": ["retrospective", "agile", "team", "improvement"],
            "is_featured": False
        }
    ]

    async with async_session_factory() as db:
        for wf in workflows:
            await db.execute(
                text("""
                    INSERT INTO workflow_templates
                    (title, description, workflow_type, steps, prompts, expected_duration_minutes,
                     icon, difficulty, tags, is_featured)
                    VALUES (:title, :desc, :type, :steps, :prompts, :duration, :icon, :diff, :tags, :featured)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "title": wf["title"],
                    "desc": wf["description"],
                    "type": wf["workflow_type"],
                    "steps": wf["steps"],
                    "prompts": wf["prompts"],
                    "duration": wf["expected_duration_minutes"],
                    "icon": wf["icon"],
                    "diff": wf["difficulty"],
                    "tags": wf["tags"],
                    "featured": wf["is_featured"]
                }
            )
        await db.commit()


async def seed_conversation_examples():
    """Seed conversation examples into the database."""
    examples = [
        {
            "title": "Brainstorm Startup Ideas",
            "description": "Generate and evaluate potential startup ideas based on your skills and interests",
            "category": "brainstorm",
            "starter_prompt": "I want to brainstorm startup ideas. I'm interested in [your interests] and have skills in [your skills]. Can you help me generate 10 potential business ideas?",
            "example_response": "I'd be happy to help! Let's explore startup ideas that combine your interests and skills...",
            "follow_up_prompts": [
                "Which of these ideas has the most market potential?",
                "What would be the MVP for idea #3?",
                "What competitors exist in this space?",
                "How could I validate this idea with minimal investment?"
            ],
            "icon": "💼",
            "difficulty": "intermediate",
            "tags": ["entrepreneurship", "business", "ideation", "startup"],
            "is_featured": True
        },
        {
            "title": "Plan a Learning Journey",
            "description": "Create a structured path to learn a new skill from beginner to proficient",
            "category": "learning",
            "starter_prompt": "I want to learn [skill/subject]. I'm currently a [beginner/intermediate]. Can you create a 3-month learning plan with resources and milestones?",
            "example_response": "Great choice! Let's design a comprehensive learning journey...",
            "follow_up_prompts": [
                "What are the best resources for beginners?",
                "How can I practice these skills?",
                "What projects should I build?",
                "How will I know when I've reached proficiency?"
            ],
            "icon": "🎓",
            "difficulty": "beginner",
            "tags": ["learning", "education", "skill", "self-improvement"],
            "is_featured": True
        },
        {
            "title": "Research a Complex Topic",
            "description": "Deep dive into a complex subject with structured research and synthesis",
            "category": "research",
            "starter_prompt": "I need to understand [topic] deeply. Can you help me research this by outlining key concepts, current debates, and leading experts?",
            "example_response": "Let's break down this complex topic into digestible components...",
            "follow_up_prompts": [
                "What are the key papers or books on this topic?",
                "Who are the leading researchers?",
                "What are the main schools of thought?",
                "How has thinking evolved on this topic?"
            ],
            "icon": "🔍",
            "difficulty": "advanced",
            "tags": ["research", "analysis", "learning", "deep-dive"],
            "is_featured": True
        },
        {
            "title": "Daily Reflection",
            "description": "End-of-day reflection to process experiences and plan for tomorrow",
            "category": "reflection",
            "starter_prompt": "Help me reflect on my day. I'll share what happened, and you can help me identify insights, lessons, and opportunities for tomorrow.",
            "example_response": "I'd be glad to help you reflect. Please share about your day...",
            "follow_up_prompts": [
                "What patterns do you notice in my challenges?",
                "What could I have done differently?",
                "What energized me most today?",
                "What should be my top priority tomorrow?"
            ],
            "icon": "🌙",
            "difficulty": "beginner",
            "tags": ["reflection", "journaling", "mindfulness", "growth"],
            "is_featured": False
        },
        {
            "title": "Goal Setting Session",
            "description": "Set meaningful, achievable goals using the SMART framework",
            "category": "planning",
            "starter_prompt": "I want to set goals for [timeframe]. My areas of focus are [areas]. Can you help me create SMART goals and an action plan?",
            "example_response": "Let's create meaningful, achievable goals together...",
            "follow_up_prompts": [
                "How can I measure progress on these goals?",
                "What obstacles might I face?",
                "How can I break these into smaller milestones?",
                "What daily habits support these goals?"
            ],
            "icon": "🎯",
            "difficulty": "beginner",
            "tags": ["goals", "planning", "strategy", "achievement"],
            "is_featured": False
        },
        {
            "title": "Creative Writing Prompt",
            "description": "Generate creative writing ideas and develop them into stories",
            "category": "creative",
            "starter_prompt": "I want to practice creative writing. Can you give me an interesting prompt and help me develop a short story?",
            "example_response": "Here's an intriguing prompt to spark your creativity...",
            "follow_up_prompts": [
                "How can I develop this character further?",
                "What plot twist would make this more engaging?",
                "How should I structure this narrative?",
                "Can you give me feedback on this draft?"
            ],
            "icon": "✍️",
            "difficulty": "intermediate",
            "tags": ["creative", "writing", "storytelling", "fiction"],
            "is_featured": False
        }
    ]

    async with async_session_factory() as db:
        for ex in examples:
            await db.execute(
                text("""
                    INSERT INTO conversation_examples
                    (title, description, category, starter_prompt, example_response,
                     follow_up_prompts, icon, difficulty, tags, is_featured)
                    VALUES (:title, :desc, :cat, :starter, :response, :followups, :icon, :diff, :tags, :featured)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "title": ex["title"],
                    "desc": ex["description"],
                    "cat": ex["category"],
                    "starter": ex["starter_prompt"],
                    "response": ex["example_response"],
                    "followups": ex["follow_up_prompts"],
                    "icon": ex["icon"],
                    "diff": ex["difficulty"],
                    "tags": ex["tags"],
                    "featured": ex["is_featured"]
                }
            )
        await db.commit()


async def seed_all_templates():
    """Seed all template types."""
    print("Seeding project templates...")
    await seed_project_templates()
    print("Seeding workflow templates...")
    await seed_workflow_templates()
    print("Seeding conversation examples...")
    await seed_conversation_examples()
    print("Template seeding complete!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_all_templates())
