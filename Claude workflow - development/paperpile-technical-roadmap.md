# Technical Roadmap: Academic Knowledge-to-Writing System

## Project Overview
Building 6 integrated systems to bridge Paperpile → Obsidian → Writing

## System Architecture

```
[System 1: Literature Bridge] → [System 5: Workspace Organization]
           ↓                              ↓
[System 2: Reflection AI] → [System 3: Writing MPC]
           ↓                              ↓
[System 4: Discovery] → [System 6: Project Management]
```

---

## System 1: Paperpile-Obsidian Literature Bridge
**Purpose**: Synchronize 700+ articles between Paperpile and Obsidian

### Component 1: Smart Import & Sync [CURRENT FOCUS]
- **What**: Intelligent import that syncs Paperpile → Obsidian
- **Input**: `~/Desktop/paperpile.bib`
- **Output**: `/4 articles/[Author Year - Title].md`
- **Features**:
  - Create new articles
  - Update existing (preserve your edits)
  - Detect orphaned files
  - Suggest removals (never auto-delete)
  - Generate sync report
- **Status**: Ready to build

### Component 2: PDF Annotation Extraction
- **What**: Extract highlights/comments from PDFs
- **Challenge**: Annotations might be in Paperpile cloud
- **Status**: Needs investigation
- **Note**: Can be added after Component 1 works

---

## System 2: Reflection Intelligence Engine
**Purpose**: Analyze daily teaching notes for patterns

### Component 2a: Daily Note Parser
- **What**: Extract themes from daily reflections
- **Tech**: NLP, pattern matching

### Component 2b: Weekly Synthesis Generator
- **What**: AI creates weekly insight reports
- **Tech**: Claude API integration

### Component 2c: Literature Connector
- **What**: Link reflections to relevant articles
- **Tech**: Semantic similarity matching

---

## System 3: Co-Intelligence Writing Environment (MPC)
**Purpose**: Claude Desktop as writing partner

### Component 3a: Vault Access Protocols
- **What**: Give Claude structured access to Obsidian
- **Tech**: MPC file creation

### Component 3b: Context Management
- **What**: Maintain relevant context during writing
- **Tech**: Smart file selection

### Component 3c: Citation Preservation
- **What**: Keep academic citations intact
- **Tech**: Reference tracking

---

## System 4: Literature Discovery & Monitoring
**Purpose**: Find new relevant research automatically

### Component 4a: RSS Feed Integration
- **What**: Monitor journal feeds
- **Tech**: Feed parser, filtering

### Component 4b: Relevance Scoring
- **What**: Score articles based on current work
- **Tech**: ML classification

### Component 4c: Import Queue
- **What**: Queue articles for review
- **Tech**: Priority system

---

## System 5: Knowledge-to-Writing Workspace
**Purpose**: Separate reference library from active writing

### Component 5a: Folder Structure
- **What**: Knowledge Garden vs Writing Workshop
- **Tech**: File organization

### Component 5b: Project Collections
- **What**: Group literature by writing project
- **Tech**: Dynamic collections

### Component 5c: Version Control
- **What**: Track draft evolution
- **Tech**: Git integration

---

## System 6: Academic Project Management
**Purpose**: Track multiple papers/chapters

### Component 6a: Project Tracking
- **What**: Status of each writing project
- **Tech**: Project database

### Component 6b: Literature Mapping
- **What**: Link sources to arguments
- **Tech**: Relationship tracking

### Component 6c: Submission Management
- **What**: Journal requirements, deadlines
- **Tech**: Calendar integration

---

## Implementation Order

### Phase 1: Foundation (Current)
1. System 1 Component 1a ← **START HERE**
2. System 1 Component 1b
3. System 1 Component 1c
4. Test complete pipeline

### Phase 2: Intelligence
5. System 2 (all components)
6. System 3 (all components)

### Phase 3: Advanced
7. System 4 (discovery)
8. System 5 (workspace)
9. System 6 (projects)

---

## For Claude Code

When building any component, reference:
1. **This roadmap** - Where component fits
2. **Design document** - Why it matters (omdöme, reflection, etc.)
3. **Component specs** - Detailed implementation

Current task: Build System 1, Component 1a