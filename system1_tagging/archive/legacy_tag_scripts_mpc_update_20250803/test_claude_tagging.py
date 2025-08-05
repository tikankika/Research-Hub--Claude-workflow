#!/usr/bin/env python3
"""Test Claude tagging with a simple example"""

test_metadata = {
    'title': 'Using Blogging as a Tool to Further Teacher Professional Development',
    'authors': 'Hines, Mark',
    'year': '2008',
    'journal': '',
    'abstract': '''Technology has changed the way effective educators learn and work with peers and students. 
    Social interaction powerfully shapes teachers' affective and cognitive flexibility in adapting their 
    teaching methodology. Computer networks now allow adaptable social communication tools that increase 
    teachers' interactions and personal growth. This paper first looks at the research in teacher development 
    through social constructs. It then summarizes a study of teachers' first interaction with a school weblog 
    to assess whether their perceptions confirm a sense of community conversation and value. Regardless of 
    their experience prior to the use of the weblog, teachers reported ease in using it. Moreover, they felt 
    it was an important tool for campus communication. Teachers also felt that professional use of tools 
    leads to higher adoption in classroom practice. This paper concludes by considering implications of the 
    survey results and developing some recommendations for further research.''',
    'keywords': [],
    'existing_tags': [],
    'full_text': '',
    'methodology': '',
    'key_findings': 'Teachers reported ease in using weblog, felt it was important for campus communication, professional use leads to higher classroom adoption',
    'research_questions': 'How do teachers perceive school weblogs for professional development and community building?',
    'theoretical_framework': 'Social constructivism, teacher professional development',
    'implications': 'Weblogs can support teacher professional development and community building'
}

# Test tag suggestions
print("Test metadata prepared:")
print(f"Title: {test_metadata['title']}")
print(f"Abstract: {test_metadata['abstract'][:200]}...")
print(f"\nThis article should be tagged with:")
print("- #teacher_education")
print("- #professional_development") 
print("- #blogging")
print("- #educational_technology")
print("- #social_media")
print("- #online_communities")
print("- #case_study")
print("\nNow you can test this with the article tagger to see if Claude returns appropriate tags.")