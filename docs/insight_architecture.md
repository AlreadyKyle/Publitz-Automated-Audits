# Insight Architecture: Strategy vs Execution

## Overview

The Publitz audit system generates two distinct types of insights:

### 1. Strategy Insights 🎯
**Purpose**: Require human decision-making and strategic judgment
**Destination**: Project management tools (Jira, Asana, Trello)
**Action**: Create tickets/tasks for team review
**Timeline**: Review within 24-48 hours

### 2. Execution Insights ⚡
**Purpose**: Automated, data-driven actions with clear implementation paths
**Destination**: Direct system integrations via connectors
**Action**: Automated commits/updates to connected services
**Timeline**: Execute immediately or schedule for optimal timing

---

## Insight Classification Framework

### Strategy Insight Criteria
An insight is **Strategy** if it requires:
- Budget approval or allocation
- Creative/artistic decisions
- Market positioning choices
- Priority trade-offs
- Risk assessment
- Team consensus
- Legal/compliance review

### Execution Insight Criteria
An insight is **Execution** if it:
- Has objective, data-driven recommendations
- Can be automated safely
- Has clear rollback mechanisms
- Requires no creative judgment
- Has industry-standard best practices
- Can be validated programmatically

---

## Connector Architecture

### Available Connectors

#### 1. **Steam Store Connector** 🎮
**Purpose**: Update Steam store page metadata
**Actions**:
- Add/remove tags
- Update system requirements
- Modify supported languages list
- Set regional pricing
- Update store description sections (structured data only)

**Safety**:
- Preview mode before commit
- Rollback capability
- Version history
- Requires Steam API key with limited permissions

#### 2. **Email Automation Connector** 📧
**Purpose**: Send outreach campaigns
**Actions**:
- Send curator outreach emails
- Send streamer pitch emails
- Send press release emails
- Schedule follow-ups

**Safety**:
- Rate limiting (max 50/day)
- Preview all emails before send
- Unsubscribe links
- Bounce handling
- Requires explicit opt-in

#### 3. **Social Media Connector** 📱
**Purpose**: Schedule and post content
**Actions**:
- Post to Twitter/X
- Schedule Reddit posts
- Post to Discord channels
- Update community hub

**Safety**:
- Approval queue
- Scheduled posting only (no immediate)
- Delete capability within 5 minutes
- Rate limiting per platform

#### 4. **Project Management Connector** 📋
**Purpose**: Create and update tickets
**Actions**:
- Create Jira tickets
- Create Asana tasks
- Create Trello cards
- Add comments/updates
- Set priorities and assignees

**Safety**:
- No deletion capability
- Append-only updates
- Maintains audit trail

#### 5. **Data Export Connector** 📊
**Purpose**: Export to spreadsheets and databases
**Actions**:
- Update Google Sheets
- Export to CSV
- Sync to database
- Generate reports

**Safety**:
- Read-only by default
- Explicit write permissions
- Backup before overwrite

#### 6. **Analytics Connector** 📈
**Purpose**: Track metrics and performance
**Actions**:
- Log metrics to dashboard
- Set up tracking codes
- Configure UTM parameters
- Schedule metric reports

**Safety**:
- Read-only analytics data
- No user data collection
- GDPR compliant

---

## Insight Types by Category

### Store Page Optimization

| Insight | Type | Connector | Rationale |
|---------|------|-----------|-----------|
| Add missing tags | **Execution** ⚡ | Steam Store | Objective tag recommendations based on genre analysis |
| Update capsule image | **Strategy** 🎯 | Jira | Creative decision requiring designer input |
| Add 5 more screenshots | **Strategy** 🎯 | Jira | Requires capturing new game content |
| Optimize description structure | **Execution** ⚡ | Steam Store | Restructure based on proven templates |
| Set system requirements | **Execution** ⚡ | Steam Store | Technical specs from game engine |
| Update trailer | **Strategy** 🎯 | Jira | Creative production task |

### Pricing & Localization

| Insight | Type | Connector | Rationale |
|---------|------|-----------|-----------|
| Set regional pricing | **Execution** ⚡ | Steam Store | PPP-based algorithmic pricing |
| Adjust base price | **Strategy** 🎯 | Jira | Strategic positioning decision |
| Add Chinese localization | **Strategy** 🎯 | Jira | Budget allocation + translation vendor selection |
| Enable supported languages | **Execution** ⚡ | Steam Store | Mark already-translated languages |
| Set discount strategy | **Strategy** 🎯 | Jira | Business model decision |

### Influencer Outreach

| Insight | Type | Connector | Rationale |
|---------|------|-----------|-----------|
| Send curator emails (top 10) | **Execution** ⚡ | Email Automation | Pre-approved template + curated list |
| Prioritize Twitch streamer X | **Strategy** 🎯 | Jira | Requires budget approval for sponsorship |
| Export YouTube contact list | **Execution** ⚡ | Data Export | Automated CSV generation |
| Draft press release | **Strategy** 🎯 | Jira | Requires PR team review |
| Schedule follow-up emails | **Execution** ⚡ | Email Automation | Automated sequence 7 days after initial |

### Community Engagement

| Insight | Type | Connector | Rationale |
|---------|------|-----------|-----------|
| Post to r/IndieGaming | **Strategy** 🎯 | Jira | Requires crafting engaging post |
| Join 5 Discord servers | **Strategy** 🎯 | Jira | Manual relationship building |
| Schedule announcement tweet | **Execution** ⚡ | Social Media | Pre-approved template + timing |
| Export subreddit list | **Execution** ⚡ | Data Export | Automated list generation |
| Set up Steam community hub | **Execution** ⚡ | Steam Store | Enable standard hub features |

### Launch Preparation

| Insight | Type | Connector | Rationale |
|---------|------|-----------|-----------|
| Create launch checklist | **Execution** ⚡ | Project Management | Generate Jira epic + subtasks |
| Schedule marketing emails | **Execution** ⚡ | Email Automation | Mailing list campaign sequence |
| Allocate marketing budget | **Strategy** 🎯 | Jira | Financial decision |
| Set launch date | **Strategy** 🎯 | Jira | Strategic timing decision |
| Configure UTM tracking | **Execution** ⚡ | Analytics | Automated parameter setup |

### Competitor Analysis

| Insight | Type | Connector | Rationale |
|---------|------|-----------|-----------|
| Monitor competitor pricing | **Execution** ⚡ | Analytics | Scheduled price tracking |
| Adjust positioning vs Competitor X | **Strategy** 🎯 | Jira | Marketing strategy decision |
| Match competitor feature set | **Strategy** 🎯 | Jira | Game development decision |
| Export competitor analysis | **Execution** ⚡ | Data Export | Automated CSV report |

---

## Insight Data Model

### Strategy Insight Schema
```json
{
  "insight_id": "uuid",
  "type": "strategy",
  "category": "pricing|marketing|development|localization",
  "title": "Consider Chinese localization",
  "description": "Market analysis shows 35% of potential audience is in China...",
  "priority": "high|medium|low",
  "impact": "High revenue potential (+$50K estimated)",
  "effort": "High (8-12 weeks, $15K budget)",
  "deadline": "2024-03-01",
  "decision_factors": [
    "Budget availability",
    "Translation quality assurance",
    "Cultural adaptation needs"
  ],
  "destination": {
    "connector": "jira",
    "project_key": "GAME-123",
    "issue_type": "Epic",
    "assignee": "product_manager",
    "labels": ["localization", "china-market", "revenue-opportunity"]
  },
  "metadata": {
    "created_at": "2024-01-15T10:00:00Z",
    "confidence": 0.85,
    "data_sources": ["steamdb", "regional_analysis", "competitor_research"]
  }
}
```

### Execution Insight Schema
```json
{
  "insight_id": "uuid",
  "type": "execution",
  "category": "store_optimization|outreach|analytics",
  "title": "Add 5 missing genre tags",
  "description": "Analysis shows your game is missing critical discovery tags...",
  "priority": "high|medium|low",
  "auto_execute": true,
  "requires_approval": false,
  "execution": {
    "connector": "steam_store",
    "action": "add_tags",
    "parameters": {
      "tags_to_add": ["Roguelike", "Pixel Art", "Difficult", "Permadeath", "Procedural Generation"],
      "dry_run": false
    },
    "rollback": {
      "enabled": true,
      "previous_state": {
        "tags": ["Action", "Indie", "2D"]
      }
    }
  },
  "validation": {
    "checks": [
      "tag_limit_not_exceeded (current: 8, max: 20)",
      "tags_exist_in_steam_taxonomy",
      "no_duplicate_tags"
    ],
    "status": "passed"
  },
  "impact": {
    "estimated_visibility_increase": "+15-25%",
    "estimated_wishlist_increase": "+200-400 per week"
  },
  "metadata": {
    "created_at": "2024-01-15T10:00:00Z",
    "executed_at": null,
    "execution_status": "pending",
    "confidence": 0.95,
    "data_sources": ["competitor_tags", "genre_analysis", "steam_recommendations"]
  }
}
```

---

## Implementation Workflow

### Strategy Insight Workflow
```
1. Generate Insight (AI Analysis)
   ↓
2. Validate & Score Priority
   ↓
3. Create Jira Ticket
   ↓
4. Assign to Team Member
   ↓
5. Human Review & Decision
   ↓
6. Implementation (manual or separate automation)
   ↓
7. Mark Complete & Track ROI
```

### Execution Insight Workflow
```
1. Generate Insight (AI Analysis)
   ↓
2. Validate & Check Safety Rules
   ↓
3. Preview Changes (if applicable)
   ↓
4. Require Approval (if flagged)
   ↓
5. Execute via Connector
   ↓
6. Verify Success
   ↓
7. Log to Analytics
   ↓
8. Monitor Impact
```

---

## Updated Insight Language

### Strategy Insights - Decision-Oriented Language
- "**Consider** adding Chinese localization to capture 35% of market"
- "**Evaluate** pricing strategy against top 3 competitors"
- "**Decide** on marketing budget allocation across channels"
- "**Review** capsule image effectiveness vs genre standards"
- "**Assess** launch timing based on competitor release schedule"

### Execution Insights - Action-Oriented Language
- "**Add** 5 missing discovery tags: Roguelike, Pixel Art, Difficult, Permadeath, Procedural Generation"
- "**Enable** German, French, Spanish language support flags in store"
- "**Set** regional pricing for 14 markets based on PPP analysis"
- "**Send** outreach emails to 10 high-priority Steam curators"
- "**Export** YouTube channel contact list (15 creators, 2.5M combined reach)"
- "**Schedule** launch announcement tweet for Tuesday 10 AM EST"
- "**Configure** UTM tracking codes for marketing campaigns"

---

## Safety & Governance

### Execution Insight Safety Rules

1. **Preview First**: All execution insights show preview before commit
2. **Rate Limiting**: Platform-specific limits enforced
3. **Rollback Capability**: All changes reversible within 24 hours
4. **Approval Thresholds**:
   - High impact + High cost → Requires approval
   - Medium impact + Low cost → Auto-execute
   - Low impact + Low cost → Auto-execute
5. **Audit Logging**: Every execution logged with full details
6. **Error Handling**: Failed executions create Jira tickets for manual resolution

### Strategy Insight Governance

1. **Priority Scoring**: Auto-calculated based on impact/effort
2. **Deadline Setting**: Based on launch timeline
3. **Auto-Assignment**: Route to appropriate team member
4. **Follow-Up**: Auto-reminder if not actioned within 48 hours
5. **Decision Tracking**: Log final decision and rationale

---

## Metrics & Monitoring

### Execution Insight Metrics
- Success rate per connector
- Average execution time
- Rollback frequency
- Impact on KPIs (wishlists, sales, engagement)
- Cost per execution

### Strategy Insight Metrics
- Time to decision
- Implementation rate (% of insights actioned)
- ROI per insight category
- Team velocity on strategy tasks
- Insight quality score (based on outcomes)

---

## Phase Implementation Plan

### Phase 1: Foundation (Current)
- ✅ Generate both insight types
- ✅ Classify and label insights
- ✅ Export to CSV for manual execution

### Phase 2: Project Management Integration
- 🔄 Implement Jira connector
- 🔄 Auto-create tickets for strategy insights
- 🔄 Sync status updates

### Phase 3: Execution Connectors
- 📅 Steam Store connector (tags, languages, pricing)
- 📅 Data Export connector (automated CSV/sheets)
- 📅 Analytics connector (UTM codes, tracking)

### Phase 4: Communication Connectors
- 📅 Email automation connector
- 📅 Social media scheduler
- 📅 Community management tools

### Phase 5: Advanced Automation
- 📅 ML-based priority optimization
- 📅 Impact prediction models
- 📅 A/B testing framework
- 📅 Closed-loop ROI tracking
