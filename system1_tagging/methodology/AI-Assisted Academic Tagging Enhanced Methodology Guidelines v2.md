# AI-Assisted Academic Tagging: Enhanced Methodology Guidelines v2.3

## Overview
This document provides comprehensive guidelines for implementing a rigorous AI-assisted academic tagging methodology based on recommendations from methodological analysis and practical experience. The approach balances efficiency with academic credibility through systematic validation and quality control.

**Key Principle**: The tagging framework is **dynamic and content-driven**. Not every article requires tags in all categories. Quality and relevance take precedence over rigid adherence to tag counts. **8-12 tags per article** - be selective and focus on the most important elements.

**Philosophy**: With 8-12 tags allowed, every tag must earn its place. Choose tags that are:
- **Specific** rather than general
- **Informative** for finding and understanding the paper
- **Essential** to the research contribution
- **Present** in the abstract (not inferred)
- **Emerge from the content** (not forced by rules)

**Prioritization when selecting tags**:
1. Keep main topic and primary method (foundation)
2. Keep most distinctive/novel concepts
3. Keep significant findings (if clearly stated)
4. Include ethical/policy implications if prominent
5. Avoid generic or vague descriptors

## 1. Category Definitions and Coding Guidelines

### 1.1 Main Topic
**Definition**: The overarching research domain or field of study
- **Scope**: Broad disciplinary area or main focus
- **Tag Count**: 1-2 tags maximum
- **Examples**: 
  - ✓ "aied", "teacher_education", "higher_education"
  - ✗ "education" (too broad), "ai_in_higher_education" (use separate tags)

### 1.2 Key Concepts
**Definition**: Specific theories, principles, or phenomena central to the research
- **Scope**: Core conceptual building blocks used in the study
- **Tag Count**: 2-4 tags typically (can expand to 4-7 when rich content)
- **Distinction from Main Topic**: More granular than field, less specific than methods
- **Examples**:
  - ✓ "tpack", "community_of_practice", "digital_literacy"
  - ✗ "learning" (too broad), "wenger_cop_model" (too specific)

### 1.3 Methods
**Definition**: Research methodologies, analytical techniques, and experimental approaches
- **Scope**: How the research was conducted (if stated in abstract)
- **Tag Count**: 0-2 tags
- **Include**: Data collection methods, analysis techniques, research designs
- **Examples**:
  - ✓ "survey_research", "systematic_review", "mixed_methods"
  - ✗ "research" (too vague), "online_survey" (too specific)

### 1.4 Findings
**Definition**: Principal discoveries, results, conclusions, or key arguments
- **Scope**: What was learned, demonstrated, or argued
- **Tag Count**: 2-4 tags
- **Focus**: Concrete outcomes or main arguments
- **Examples**:
  - ✓ "student_optimism", "teacher_concerns", "privacy_concerns"
  - ✗ "interesting_results" (too vague), "23%_improvement" (too specific)

### 1.5 Theoretical Framework
**Definition**: Underlying theories or models explicitly guiding the research
- **Scope**: Established theories referenced or extended
- **Tag Count**: 0-1 tag
- **Note**: Often not applicable - only include if central and explicit
- **Examples**:
  - ✓ "activity_theory", "cognitive_load_theory"
  - ✗ "theoretical" (incomplete), specific model names unless central

### 1.6 Potential Applications
**Definition**: Practical uses, implications, or contexts of the research
- **Scope**: Real-world applications, policy implications, educational contexts
- **Tag Count**: 1-3 tags
- **Examples**:
  - ✓ "policy_implications", "science_education", "higher_education"
  - ✗ "could_be_useful" (too vague)

## 2. Tag Naming Conventions

### 2.1 Compound vs Separate Tags
**Principle**: Avoid redundant compound tags when domain tags exist
- Use: `aied` + `teaching_planning` NOT `ai_teaching_planning`
- Use: `aied` + `teacher_roles` NOT `teacher_roles_in_ai`
- Use: `tpack` alone, NOT `tpack_improvement` or `tpack_framework`
- Exception: Established compounds like `digital_literacy`, `higher_education`

### 2.2 Abbreviations and Terminology
**Common abbreviations (use these when applicable):**
- `genai` (not generative_ai)
- `tpd` (teacher professional development)
- `aied` (AI in education)
- `cscl` (computer-supported collaborative learning)
- `ict` (information and communication technology)
- `mooc` (massive open online course)

### 2.3 Theory and Model References
**Guidelines for theoretical tags:**
- Use general theory names, not specific researcher attributions
- Only include if central to the paper's contribution
- Examples:
  - Use: `community_of_practice` NOT `wenger_cop_model`
  - Use: `constructivism` NOT `piaget_constructivism`

## 3. Reliability Testing Protocol

### 3.1 Initial Calibration (One-time setup)
1. Select 20 articles across different domains
2. Tag each article twice with 24-hour interval
3. Calculate intra-rater reliability (target: >80% consistency)
4. Document and resolve inconsistencies

### 3.2 Ongoing Validation
1. **Weekly**: Dual-code 10% of new articles (AI + manual)
2. **Monthly**: Calculate Cohen's Kappa (acceptable: ≥0.70)
3. **Quarterly**: Full methodology review and refinement

### 3.3 Disagreement Resolution
- Document all AI-human disagreements
- Identify patterns in disagreements
- Update prompts/guidelines to address systematic issues
- Maintain disagreement log for transparency

## 4. Controlled Vocabulary Development

**Philosophy**: Vocabularies should **emerge from the literature**, not control it. The goal is consistency in your own tagging, not forcing papers into predetermined categories.

**Important**: These vocabulary lists are **suggestive, not prescriptive**. They serve as examples and starting points to ensure consistency, but should not limit or constrain tagging. New terms should emerge naturally from the literature.

### 4.1 Sample Vocabulary Lists (Expand as Needed)

#### AI/Technology Terms
```
Common terms - add new ones as they appear:
- aied
- genai
- chatgpt
- machine_learning
- deep_learning
- ai_chatbots
- personalized_learning
- automated_assessment
- learning_analytics
- educational_data_mining
[Expand based on literature]
```

#### Research Methods
```
Frequently seen - not exhaustive:
- survey_research
- mixed_methods
- systematic_review
- case_study
- quantitative_research
- qualitative_research
- design_based_research
- action_research
[Add methods as encountered]
```

#### Educational Contexts
```
Common contexts - let vocabulary grow:
- higher_education
- k12_education
- teacher_education
- tpd
- online_learning
- blended_learning
- distance_education
- informal_learning
[New contexts emerge regularly]
```

#### Stakeholder Perspectives
```
Observed patterns - expand freely:
- student_perceptions
- teacher_concerns
- student_attitudes
- teacher_beliefs
- parental_involvement
- administrator_perspectives
[Add as relevant]
```

#### Ethical and Policy Terms
```
Growing area - stay current:
- ai_ethics
- ethical_concerns
- privacy_concerns
- responsible_ai_use
- policy_implications
- digital_divide
- algorithmic_bias
- data_protection
[Field evolving rapidly]
```

### 4.2 Synonym Management
**Purpose**: Track equivalent terms for consistency, not to restrict vocabulary.

**General Examples:**
- "machine_learning" = "ml" (use full term)
- "artificial_intelligence" = "ai" (context dependent)
- "higher_education" = "university" = "tertiary_education"

**Note**: If authors use a specific variant, consider keeping their terminology. Synonym tracking is for your own consistency across articles.

## 5. Documentation Standards

### 5.1 AI Configuration Documentation
```markdown
## Tagging Session Details
- Date: [YYYY-MM-DD]
- AI Model: Claude Desktop [version]
- Articles processed: [number]
- Time per article: [average in minutes]

## Prompt Used
[Exact prompt text including any modifications]

## Modifications Made
- [List any prompt adjustments during session]
- [Reason for each modification]
```

### 5.2 Article Processing Log
```markdown
## Article ID: [identifier]
- Title: [full title]
- Tagging method: [Abstract-only / Full-text sample]
- Confidence level: [High/Medium/Low]
- Manual modifications: [Yes/No - details if yes]
- Time spent: [minutes]
- Notes: [any uncertainties or special considerations]
```

## 6. Quality Assurance Workflow

### 6.1 Standard Processing Flow
```
1. AI Initial Tagging (1-2 min)
   - Use standardized prompt
   - Save raw AI output
   
2. Human Review & Modification (2-3 min)
   - **Verify tags match abstract content**
   - **Check for compound tag opportunities**
   - **Ensure 8-12 total tags**
   - **Remove any inferred content**
   - **Consider established vocabulary for consistency**
   
3. Consistency Check (30 sec)
   - Note synonym usage
   - Check abbreviation standards
   - Verify category appropriateness
   
4. Documentation (30 sec)
   - Note confidence level
   - Flag unusual cases
```

**Total time: 4-6 minutes per article**

### 6.2 Enhanced Error Prevention Checklist
- [ ] Used 8-12 tags total
- [ ] Avoided redundant compound tags
- [ ] Used established abbreviations where applicable
- [ ] Included method tags only when stated
- [ ] Separated AI/domain tags from general concepts
- [ ] Checked for existing similar tags before creating new ones
- [ ] All tags derived from abstract content
- [ ] No overly specific theoretical references

### 6.3 Category Checklist - IMPORTANT
**Always review ALL six categories:**
- [ ] Main Topic (1-2 tags)
- [ ] Key Concepts (2-4 tags, can expand to 4-7 when rich content)
- [ ] Methods (0-2 tags - only if stated)
- [ ] Findings/Arguments (2-4 tags)
- [ ] **Theoretical Framework (0-1 tag) - DO NOT SKIP**
- [ ] Potential Applications (1-3 tags)

**Note:** Even if a category doesn't apply, consciously check it. Theoretical frameworks are often implicit and should be identified when possible.

## 7. Implementation Guidelines

### 7.1 When to Skip Categories
- **Methods**: Skip if not explicitly mentioned in abstract
- **Findings**: For position/perspective papers, use key arguments instead
- **Theoretical Framework**: Only if explicitly named and central
- **Relevance for High School**: Usually skip for higher ed focused papers

### 7.2 Tag Distribution Guidelines (Flexible)
- Main Topic: 1-2 tags
- Key Concepts: 2-4 tags
- Methods: 0-2 tags
- Findings/Arguments: 2-4 tags
- Theoretical Framework: 0-1 tag
- Applications/Context: 1-3 tags

## 8. Special Cases Handling

### 8.1 Books Without Abstracts
**When encountering books:**
- **Primary approach**: Skip entirely - mark as "Skipped - no abstract available"
- **Do NOT attempt minimal tagging**
- **Move to next item in collection**
- **Document in processing log for completeness**

### 8.2 Conference Papers Without Abstracts
**For conference proceedings:**
- Check if extended abstract exists
- Use presentation title and session theme
- Tag more conservatively (5-7 tags max)
- Note: "conference_paper_no_abstract"

### 8.3 Non-English Abstracts
**When abstract is in another language:**
- If English translation provided: use that
- If keywords in English: use those cautiously
- Otherwise: skip or mark for later review
- Document: "non_english_abstract"

### 8.4 Missing or Corrupted Abstracts
**When abstract section is empty or corrupted:**
- Check if abstract exists elsewhere in document
- Do NOT infer from introduction or conclusion
- Mark as "missing_abstract" and skip
- Flag for manual review if critical paper

### 8.5 Skip Policy Summary
**Always skip when:**
1. No abstract available (books, conference papers)
2. Abstract is corrupted or missing
3. Abstract is in non-English language without translation
4. Document type cannot be determined

**Mark skipped items with:**
- "Skipped - no abstract available"
- "Skipped - non-English abstract"
- "Skipped - corrupted data"
- Include in processing log for transparency

## 9. Common Tagging Patterns (Observations)

**Note**: These are patterns observed in practice, not rules. Let the abstract content guide your tagging.

### For AI in Education Papers:
- **Often includes** `aied` or `genai` depending on focus
- **May feature** specific tools if prominently discussed (e.g., `chatgpt`)
- **Consider** stakeholder perspectives when emphasized
- **Look for** ethical concerns or policy implications

### For Teacher Professional Development:
- **Typically uses** `tpd` or `teacher_education`
- **May include** specific competencies (e.g., `tpack`, `digital_competence`)
- **Consider** participant descriptors if relevant
- **Look for** delivery methods (e.g., `online_learning`, `workshops`)

### For Research Papers:
- **Include method tags when explicitly stated**
- **Remember** not all abstracts mention methods
- **For reviews**: often `systematic_review` or `literature_review`
- **For empirical**: method depends on abstract content

### For Student-Focused Research:
- **Often includes** `student_perceptions` or similar
- **May feature** learning outcomes or engagement
- **Consider** educational level if specified
- **Look for** technology acceptance themes

## 10. Continuous Improvement Protocol

### Monthly Review Questions
1. What new terms emerged that need vocabulary inclusion?
2. Which tag combinations appeared frequently?
3. What patterns in AI suggestions need adjustment?
4. Are there new abbreviations to standardize?

### Quarterly Methodology Audit
- Recalculate reliability metrics
- Update controlled vocabularies
- Review and refine category definitions
- Incorporate feedback from usage
- Benchmark against new literature trends

## 11. Limitations and Transparency

### Acknowledged Limitations
1. **Abstract-only analysis**: May miss methodological nuances
2. **AI variability**: Output may vary between sessions
3. **Domain evolution**: New concepts emerge regularly
4. **Language constraints**: English-language bias in tagging

### Transparency Requirements
- Always note: "Tagged using AI-assisted methodology"
- Specify: "Based on abstract analysis" when applicable
- Maintain audit trail of decisions
- Document any significant departures from guidelines

## Appendix A: Sample AI Prompt Template

```
Please analyze this academic abstract and provide tags in the following categories. Only include categories where relevant information is clearly present in the abstract. Use 8-12 total tags - be selective and prioritize the most important elements.

1. Main Topic (1-2 tags): The broad research field or focus
2. Key Concepts (2-4 tags): Essential theories, principles, or phenomena  
3. Methods (0-2 tags): Research methodology if explicitly mentioned
4. Findings (2-4 tags): Most significant results or key arguments
5. Theoretical Framework (0-1 tag): Main theory if explicitly mentioned or clearly implied
6. Potential Applications (1-3 tags): Clear contexts, implications, or uses

Guidelines:
- Use established abbreviations: aied, genai, tpd, cscl
- Avoid compound tags when separate tags work (e.g., aied + assessment, not ai_assessment)
- Be specific but not overly detailed
- All tags must be derived from abstract content
- Quality over quantity - fewer precise tags are better than many vague ones

Abstract: [INSERT ABSTRACT TEXT]
```

## Appendix B: Version History

**v2.0 (Initial Enhanced Version)**
- Based on practical tagging experience
- Established 8-12 tag range
- Added tag naming conventions
- Created initial controlled vocabularies

**v2.1 (Special Cases Added)**
- Added Section 8: Special Cases Handling
- Initially allowed minimal tagging for books without abstracts
- Added handling for conference papers, non-English abstracts

**v2.2 (Skip Policy Update)**
- Changed approach: skip all items without abstracts
- No minimal tagging attempts
- Updated Section 8.5 with skip policy summary

**v2.3 (Current Version)**
- Added Section 6.3: Category Checklist
- Emphasized Theoretical Framework category (often forgotten)
- Fixed tag count inconsistencies
- Added version history

---

*Version 2.3 - Added category checklist to ensure Theoretical Framework is not forgotten*
*This document should be treated as a living guide, updated regularly based on empirical findings and methodological advances in AI-assisted content analysis.*