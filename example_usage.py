"""
Example usage of the EPUB Agent Skill.

This script demonstrates how to use the EPUB Agent Skill to process an EPUB file
and extract structured outlines and chapter summaries.
"""

from epub_agent_skill.main import skill


def main():
    """
    Example of using the EPUB Agent Skill.
    """
    # Replace with the path to your EPUB file
    epub_file_path = "sample_book.epub"
    
    try:
        # Call the skill function with the path to the EPUB file
        result = skill(epub_file_path)
        
        # Print the extracted metadata
        print("Book Metadata:")
        for key, value in result['metadata'].items():
            print(f"  {key}: {value}")
        print()
        
        # Print the outline
        print("Book Outline:")
        for item in result['outline']:
            print(f"  {item['order'] + 1}. {item['title']}")
        print()
        
        # Print the summaries
        print("Chapter Summaries:")
        for summary_item in result['summaries']:
            print(f"  Chapter {summary_item['order'] + 1}: {summary_item['chapter_title']}")
            print(f"    Summary: {summary_item['summary'][:100]}...")
            print()
    
    except FileNotFoundError:
        print(f"Error: Could not find the EPUB file at {epub_file_path}")
        print("Please make sure the file exists and the path is correct.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()