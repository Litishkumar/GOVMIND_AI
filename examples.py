"""
GovMind AI Module - Example Usage
Demonstrates various ways to use the routing system
"""

from main import GovMindAI, route_complaint, route_complaints_batch
import json
from loguru import logger

# Configure minimal logging for examples
logger.remove()
logger.add(lambda msg: None)  # Suppress logs


def example_1_simple_routing():
    """Example 1: Simple complaint routing"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple Complaint Routing")
    print("="*80 + "\n")
    
    complaint = "There is no electricity in my area for the past 8 hours"
    
    print(f"Complaint: {complaint}\n")
    
    result = route_complaint(complaint, use_llm=True)
    
    print("Routing Result:")
    print(f"  Department: {result['department']}")
    print(f"  Category: {result['category']}")
    print(f"  Priority: {result['priority']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Reason: {result['reason']}")


def example_2_tamil_complaint():
    """Example 2: Tamil language complaint"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Tamil Language Support")
    print("="*80 + "\n")
    
    complaint = "எங்கள் பகுதியில் தண்ணீர் வருவதில்லை. ஒரு வாரமாக பிரச்சனை உள்ளது"
    
    print(f"Complaint (Tamil): {complaint}\n")
    
    result = route_complaint(complaint, use_llm=True)
    
    print("Routing Result:")
    print(f"  Department: {result['department']}")
    print(f"  Priority: {result['priority']}")
    print(f"  Confidence: {result['confidence']}")


def example_3_batch_processing():
    """Example 3: Batch complaint processing"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Batch Processing")
    print("="*80 + "\n")
    
    complaints = [
        "Power outage affecting entire neighborhood",
        "Water supply interrupted for 3 days",
        "Garbage collection missed for one week",
        "Large pothole on main road causing accidents",
        "Noise pollution from construction at night"
    ]
    
    print(f"Processing {len(complaints)} complaints...\n")
    
    results = route_complaints_batch(complaints)
    
    print("Results Summary:")
    print("-" * 80)
    for i, item in enumerate(results, 1):
        if item['status'] == 'success':
            result = item['result']['routing_decision']
            print(f"{i}. {result['department']} - {result['priority']} priority")
        else:
            print(f"{i}. ERROR: {item['error']}")


def example_4_detailed_output():
    """Example 4: Accessing detailed routing information"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Detailed Routing Information")
    print("="*80 + "\n")
    
    ai_system = GovMindAI(initialize_db=False)
    
    complaint = "Emergency! Major water pipeline burst flooding the entire street"
    
    print(f"Complaint: {complaint}\n")
    
    # Get full detailed result
    result = ai_system.route(complaint, use_llm=True, return_format="full")
    
    print("1. ROUTING DECISION:")
    print(f"   Department: {result['routing_decision']['department']}")
    print(f"   Category: {result['routing_decision']['category']}")
    print(f"   Priority: {result['routing_decision']['priority']}")
    
    print("\n2. CLASSIFICATION DETAILS:")
    primary = result['classification']['primary_department']
    print(f"   Similarity Score: {primary['similarity']:.4f}")
    print(f"   Confidence: {primary['confidence']}")
    print(f"   Ambiguous: {result['classification']['is_ambiguous']}")
    
    print("\n3. TOP 3 DEPARTMENTS:")
    for i, dept in enumerate(result['classification']['top_3_departments'], 1):
        print(f"   {i}. {dept['name']}: {dept['similarity']:.4f} ({dept['confidence']})")
    
    print("\n4. RETRIEVED POLICIES:")
    for i, policy in enumerate(result['retrieved_policies'][:2], 1):
        print(f"   Policy {i} (Relevance: {policy['relevance']:.4f}):")
        print(f"   {policy['text'][:100]}...")
    
    print("\n5. PRIORITY ANALYSIS:")
    priority = result['priority_analysis']
    print(f"   Suggested: {priority['suggested_priority']}")
    print(f"   Reasoning: {priority['reasoning']}")
    
    print("\n6. PROCESSING METADATA:")
    meta = result['metadata']
    print(f"   Processing Time: {meta['processing_time_seconds']:.2f}s")
    print(f"   LLM Used: {meta['llm_used']}")
    print(f"   Timestamp: {meta['timestamp']}")


def example_5_emergency_detection():
    """Example 5: Emergency and priority detection"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Emergency Priority Detection")
    print("="*80 + "\n")
    
    test_cases = [
        ("Critical: Power outage affecting hospital emergency ward", "High"),
        ("Electricity bill seems incorrect this month", "Low"),
        ("Water supply disrupted for multiple days in our area", "Medium"),
        ("Urgent: Major road accident due to pothole", "High")
    ]
    
    for complaint, expected_priority in test_cases:
        result = route_complaint(complaint, use_llm=True)
        
        match = "✓" if result['priority'] == expected_priority else "✗"
        print(f"{match} Priority: {result['priority']} | {complaint[:60]}...")


def example_6_multilingual_comparison():
    """Example 6: Compare English and Tamil routing"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Multilingual Routing Comparison")
    print("="*80 + "\n")
    
    # Similar complaints in different languages
    complaints = [
        ("English", "No water supply in our area for 5 days"),
        ("Tamil", "எங்கள் பகுதியில் 5 நாட்களாக தண்ணீர் வருவதில்லை")
    ]
    
    results = []
    for lang, complaint in complaints:
        result = route_complaint(complaint, use_llm=True)
        results.append((lang, result))
        
        print(f"{lang} Complaint:")
        print(f"  Text: {complaint}")
        print(f"  Department: {result['department']}")
        print(f"  Priority: {result['priority']}")
        print(f"  Confidence: {result['confidence']}\n")
    
    # Check if both routed to same department
    if results[0][1]['department'] == results[1][1]['department']:
        print("✓ Both complaints correctly routed to same department!")


def example_7_error_handling():
    """Example 7: Handling various input scenarios"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Error Handling and Edge Cases")
    print("="*80 + "\n")
    
    test_cases = [
        ("Valid complaint", "Street light not working"),
        ("Very short", "No water"),
        ("Mixed language", "Power cut உள்ளது"),
        ("Vague", "Problem in my area"),
    ]
    
    for description, complaint in test_cases:
        try:
            result = route_complaint(complaint, use_llm=True)
            print(f"✓ {description}: Routed to {result['department']}")
        except Exception as e:
            print(f"✗ {description}: Error - {str(e)[:50]}")


def example_8_save_results():
    """Example 8: Saving results to file"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Saving Results to JSON File")
    print("="*80 + "\n")
    
    complaints = [
        "Electricity outage",
        "Water leakage",
        "Garbage overflow"
    ]
    
    results = []
    for complaint in complaints:
        result = route_complaint(complaint, use_llm=True)
        results.append({
            "complaint": complaint,
            "department": result['department'],
            "priority": result['priority'],
            "confidence": result['confidence']
        })
    
    # Save to file
    output_file = "example_routing_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(results)} results to {output_file}")
    print(f"\nSample output:")
    print(json.dumps(results[0], indent=2))


def main():
    """Run all examples"""
    print("\n" + "#"*80)
    print("#" + " "*20 + "GovMind AI - Usage Examples" + " "*20 + "#")
    print("#"*80)
    
    examples = [
        example_1_simple_routing,
        example_2_tamil_complaint,
        example_3_batch_processing,
        example_4_detailed_output,
        example_5_emergency_detection,
        example_6_multilingual_comparison,
        example_7_error_handling,
        example_8_save_results
    ]
    
    print("\nSelect example to run:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example.__doc__.strip()}")
    print(f"  {len(examples) + 1}. Run all examples")
    print("  0. Exit")
    
    while True:
        try:
            choice = input("\nEnter choice (0-9): ").strip()
            
            if choice == "0":
                print("\nGoodbye!")
                break
            
            choice_num = int(choice)
            
            if choice_num == len(examples) + 1:
                # Run all
                for example in examples:
                    example()
                    input("\nPress Enter to continue...")
                break
            elif 1 <= choice_num <= len(examples):
                examples[choice_num - 1]()
                input("\nPress Enter to continue...")
            else:
                print("Invalid choice!")
        
        except ValueError:
            print("Please enter a valid number!")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
