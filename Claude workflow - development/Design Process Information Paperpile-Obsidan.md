# Project: Academic Knowledge-to-Writing System

## 1. Problem Statement

**Current Situation:**
As a practitioner-researcher with 20+ years teaching experience pursuing a PhD, I face a fundamental challenge: My knowledge exists in three disconnected spaces:
- **Reading & Literature** (trapped in Paperpile)
- **Thinking & Reflection** (scattered in Obsidian daily notes)
- **Writing & Synthesis** (struggling to emerge)

**The Core Problem:**
I lack a **co-intelligent system** that bridges these spaces to support the development of *omdöme* (professional judgment) - the deep wisdom that emerges from practice but needs theoretical grounding. Without this bridge, I cannot fully leverage my unique position as someone who understands teaching from the inside while developing research capabilities.

**Why This Matters:**
- **Academic Impact**: My practitioner insights could contribute to educational research if properly connected to literature
- **Personal Development**: I need to develop my research voice while honoring my teaching wisdom
- **Field Contribution**: The education field needs more practitioner-researchers who can bridge theory-practice gaps
- **Methodological Innovation**: Co-intelligence with AI could pioneer new forms of academic knowledge creation

**The Design Challenge:**
Create a system that doesn't just manage information, but actively supports **extended thinking** - where AI becomes a partner in developing insights from the interplay of practice, reflection, and literature.

## 2. Theoretical Framework

**Foundational Concepts:**

**A. Omdöme and Professional Judgment (Jonna Bornemark)**
- Swedish concept of judgment that transcends rule-following
- Essential for education where human complexity defies algorithms
- Develops through reflective practice, not just knowledge accumulation
- *Design Implication*: System must support judgment development, not replace it

**B. Multiple Ways of Knowing (Aristotelian Framework)**
- **Episteme** (scientific knowledge): What literature provides
- **Techne** (craft knowledge): Teaching methods and techniques  
- **Phronesis** (practical wisdom): Knowing what to do in specific situations
- **Sophia** (theoretical wisdom): Deep understanding of principles
- **Nous** (intuitive grasp): Immediate insight from experience
- *Design Implication*: System must integrate all forms, not privilege episteme

**C. Extended Mind & Co-Intelligence (Clark & Chalmers + Emerging AI Theory)**
- Cognition extends beyond the brain into tools and environment
- AI as cognitive partner, not replacement
- Co-intelligence emerges from human-AI collaboration
- *Design Implication*: Design for dialogue and emergence, not automation

**D. Reflective Practice & Knowledge Creation (Schön + Nonaka)**
- **Schön's Reflection-in/on-action**: Learning from practice
- **Nonaka's SECI Model**: 
  - Socialization (tacit to tacit): Teaching experiences
  - Externalization (tacit to explicit): Daily reflections
  - Combination (explicit to explicit): Literature synthesis
  - Internalization (explicit to tacit): Developing omdöme
- *Design Implication*: Support full cycle, emphasize externalization

**Theoretical Synthesis:**
This system represents a new form of **digitally-mediated phronesis development**.

## 3. Stakeholders
* **Primary**: Niklas (researcher/practitioner)
* **Secondary**: Future readers of publications
* **Constraints**: Technical (Python, Obsidian, Paperpile), Time (PhD workload), Ethical (maintain authentic voice)

## 4. Functional Requirements

### Core Systems the Solution Must Provide:

**System 1: Paperpile-Obsidian Literature Bridge**

This is ONE INTEGRATED SYSTEM that performs a complete literature synchronization workflow:

```
[Paperpile Library] → [BibTeX Export] → [Parse & Extract] → [Obsidian Vault]
                            ↓
                    [PDF Annotations]
                            ↓
                    [Searchable Notes]
                            ↓
                    [Synchronized State]
```

**The system MUST do ALL of these together:**
- Import BibTeX metadata from Paperpile export AND
- Extract PDF annotations and YOUR comments AND  
- Create/update markdown files in `/4 articles/` AND
- Link PDFs to `/9 paperpile/` folder AND
- Compare vault against library to identify orphaned files AND
- Suggest articles to remove (never auto-delete) AND
- Handle 700+ articles efficiently AND
- Make all annotations searchable

**This is NOT three separate functions - it's one pipeline where each part depends on the others.**

---

**System 2: Reflection Intelligence Engine**
(Standalone system)
- Analyze daily notes for emerging patterns
- Connect reflections to relevant literature automatically
- Generate weekly synthesis reports
- Surface insights you haven't consciously noticed
- Track development of omdöme over time

**System 3: Co-Intelligence Writing Environment (MPC)**
(Standalone system)
- Create structured protocols for Claude Desktop access
- Maintain full vault context during writing sessions
- Support argument development from notes to draft
- Preserve citation integrity throughout
- Maintain authentic practitioner-researcher voice

**System 4: Literature Discovery & Monitoring**
(Standalone system)
- Track new publications in your research domains
- Alert when relevant articles appear
- Auto-suggest papers based on current writing focus
- Queue promising articles for review

**System 5: Knowledge-to-Writing Workspace**
(Enhances Systems 1-3)
- Separate "knowledge garden" from "writing workshop"
- Maintain project-specific literature collections
- Track which sources support which arguments
- Version control for evolving drafts

**System 6: Academic Project Management**
(Coordinates all systems)
- Track multiple articles/chapters simultaneously
- Link specific literature to specific sections
- Manage submission requirements and deadlines
- Monitor progress through publication pipeline

## 5. Non-functional Requirements
* **Performance**: Sync within 2 minutes
* **Usability**: One-command execution
* **Reliability**: No data loss, versioning
* **Flexibility**: Accommodate workflow evolution

## 6. Domain Model

```
PAPERPILE (Literature Source)
    ↓ [import + annotations]
    
KNOWLEDGE GARDEN (Reference Space)
├── /4 articles/ (all literature)
├── /9 paperpile/ (PDFs)
├── Daily Reflections
└── Literature Discovery
    ↓ [selection for project]
    
WRITING WORKSHOP (Active Projects)
├── Current Drafts
├── Project Literature Sets
├── Argument Maps
└── MPC Components
    ↓ [co-intelligence]
    
CLAUDE DESKTOP (Writing Partner)
    ↕ [dialogue + context]
    
ACADEMIC OUTPUT
├── Journal Articles
├── Book Chapters
└── PhD Thesis
```

## 7. Design Decisions

### Academic Rationale for Key Design Choices:

1. **Bottom-up approach**: Patterns emerge from practice
   * *Rationale*: Aligns with practitioner research methodology where theory emerges from practice (Schön)
   * *Justification*: My 20+ years teaching experience contains tacit knowledge that needs emergence, not imposition

2. **Reflection-first**: Daily notes drive insight generation  
   * *Rationale*: Based on reflective practice theory (Schön) and externalization of tacit knowledge (Nonaka)
   * *Justification*: Daily reflections capture omdöme in development

3. **Human-in-the-loop**: AI assists, doesn't automate
   * *Rationale*: Preserves phronesis and professional judgment (Aristotle, Bornemark)
   * *Justification*: Educational decisions require human wisdom that AI cannot replace

4. **Modular architecture**: Start simple, evolve based on use
   * *Rationale*: Follows design-based research methodology in education
   * *Justification*: System must adapt to emerging understanding of practitioner-researcher needs

5. **Preserve authentic voice**: Enhance, don't replace my perspective
   * *Rationale*: Practitioner research values insider perspective and lived experience
   * *Justification*: My unique position as teacher-researcher is the value I bring

## 8. Evaluation Criteria

### How We'll Know the System Succeeds:

1. **Quality of insights from reflection analysis**
   * *Measure*: At least one unexpected connection per week between practice and literature
   * *Evidence*: Document insights that emerge from AI analysis of reflections

2. **Time saved in literature management**
   * *Measure*: Reduce manual reference work from hours to minutes
   * *Evidence*: Zero manual copying of references; find any annotation in <30 seconds

3. **Coherence of AI-assisted writing**
   * *Measure*: First draft completed in days not weeks
   * *Evidence*: Track time from idea to submittable draft

4. **Preservation of practitioner voice**
   * *Measure*: Readers recognize authentic classroom experience in writing
   * *Evidence*: Peer feedback confirms voice remains genuine

5. **Joy in the research process**
   * *Measure*: Daily use feels energizing not draining
   * *Evidence*: Continued engagement with system over time

## 9. AI Collaboration Guidelines

### Clear Division of Responsibilities:

**Human (Niklas) Responsibilities:**
* Daily reflection and observation of practice
* Exercise omdöme (professional judgment) on all suggestions
* Make final decisions on what to include/exclude
* Maintain authentic practitioner perspective
* Validate AI interpretations against lived experience

**AI Responsibilities:**
* Remember connections across all documents
* Detect patterns in reflections I might miss
* Suggest relevant literature for practice observations
* Maintain citation accuracy and formatting
* Ask probing questions to deepen thinking

**Validation Points (Human Review Required):**
* Weekly synthesis reports - confirm AI understood reflections correctly
* Literature connections - verify suggested links make sense
* Writing drafts - ensure voice remains authentic
* Any deletion suggestions - never auto-delete
* Pattern detection - validate against teaching experience

## 10. Next Steps in Design Process

Following Wieringa's Engineering Cycle, we have completed:
- ✓ **Problem Investigation** (Sections 1-2)
- ✓ **Treatment Design** (Sections 3-9, now with 6 integrated systems)

**System 1 is the Foundation:**
The Paperpile-Obsidian Literature Bridge must work as an integrated whole before other systems can build upon it.

**Suggested Implementation Steps:**
1. **Step 1**: System 1 - Complete literature synchronization pipeline
2. **Step 2**: Systems 2-3 - Add intelligence and writing support
3. **Step 3**: Systems 4-6 - Advanced features for sustained research

Next phases:
- **Treatment Validation**: Test if this design would work
- **Treatment Implementation**: Build incrementally in Windsurf
- **Implementation Evaluation**: Assess real-world effectiveness

Ready to validate System 1 as an integrated whole?