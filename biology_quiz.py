import json
import random
import os
from collections import defaultdict

class BiologyQuiz:
    def __init__(self, quiz_file="quiz_data.json"):
        self.quiz_file = quiz_file
        self.quiz_data = {}
        self.disabled_chapters = set()
        self.user_stats = defaultdict(lambda: {"correct": 0, "incorrect": 0})
        self.load_quiz_data()
    
    def load_quiz_data(self):
        """Load quiz data from a JSON file"""
        try:
            with open(self.quiz_file, 'r') as file:
                data = json.load(file)
                # Add weight to each question if not present
                for chapter, questions in data.items():
                    for question in questions:
                        if "weight" not in question:
                            question["weight"] = 1.0
                self.quiz_data = data
                print(f"Successfully loaded quiz data from {self.quiz_file}")
        except FileNotFoundError:
            print(f"Quiz file {self.quiz_file} not found.")
            self.create_sample_data()
        except json.JSONDecodeError:
            print(f"Error reading the quiz file {self.quiz_file}. Invalid JSON format.")
            self.create_sample_data()

    def create_sample_data(self):
        """Create sample data if file not found"""
        print("Creating sample quiz data...")
        self.quiz_data = {
            "Sample Chapter 1": [
                {
                    "question": "What is the powerhouse of the cell?",
                    "options": ["Nucleus", "Mitochondria", "Golgi apparatus", "Endoplasmic reticulum"],
                    "correct_option": "Mitochondria",
                    "weight": 1.0
                }
            ],
            "Sample Chapter 2": [
                {
                    "question": "What is the process by which plants make their food?",
                    "options": ["Respiration", "Photosynthesis", "Transpiration", "Digestion"],
                    "correct_option": "Photosynthesis",
                    "weight": 1.0
                }
            ]
        }
        self.save_quiz_data()

    def save_quiz_data(self):
        """Save quiz data to JSON file"""
        with open(self.quiz_file, 'w') as file:
            json.dump(self.quiz_data, file, indent=2)
        print(f"Quiz data saved to {self.quiz_file}")

    def list_chapters(self):
        """List all available chapters"""
        print("\nAvailable Chapters:")
        for i, chapter in enumerate(self.quiz_data.keys(), 1):
            status = "Disabled" if chapter in self.disabled_chapters else "Enabled"
            print(f"{i}. {chapter} [{status}]")
    
    def toggle_chapter(self, chapter_idx):
        """Enable or disable a chapter"""
        chapters = list(self.quiz_data.keys())
        if 1 <= chapter_idx <= len(chapters):
            chapter = chapters[chapter_idx - 1]
            if chapter in self.disabled_chapters:
                self.disabled_chapters.remove(chapter)
                print(f"Enabled: {chapter}")
            else:
                self.disabled_chapters.add(chapter)
                print(f"Disabled: {chapter}")
        else:
            print("Invalid chapter number!")

    def select_question(self, chapter):
        """Select a question based on weights"""
        if chapter in self.disabled_chapters:
            return None
            
        questions = self.quiz_data[chapter]
        if not questions:
            return None
            
        # Calculate total weight
        total_weight = sum(q["weight"] for q in questions)
        if total_weight == 0:
            # If all weights are 0, select with equal probability
            return random.choice(questions)
            
        # Random number between 0 and total weight
        r = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        # Select based on weight
        for question in questions:
            cumulative_weight += question["weight"]
            if r <= cumulative_weight:
                return question
                
        return questions[-1]  # Fallback

    def ask_question(self, question):
        """Present a question to the user and get their answer"""
        print(f"\n{question['question']}")
        for i, option in enumerate(question['options'], 1):
            print(f"{i}. {option}")
        
        while True:
            try:
                choice = int(input("\nEnter your choice (number): "))
                if 1 <= choice <= len(question['options']):
                    selected_option = question['options'][choice - 1]
                    correct = selected_option == question['correct_option']
                    
                    if correct:
                        print("✓ Correct!")
                        # Decrease weight (show less often)
                        question["weight"] = max(0.1, question["weight"] - 0.3)
                        self.user_stats[question["question"]]["correct"] += 1
                    else:
                        print(f"✗ Incorrect. The correct answer is: {question['correct_option']}")
                        # Increase weight (show more often)
                        question["weight"] += 0.5
                        self.user_stats[question["question"]]["incorrect"] += 1
                    
                    return correct
                else:
                    print(f"Please enter a number between 1 and {len(question['options'])}")
            except ValueError:
                print("Please enter a valid number")

    def study_chapter(self, chapter):
        """Study a specific chapter"""
        print(f"\n--- Studying: {chapter} ---")
        
        question_count = 0
        correct_count = 0
        
        while True:
            question = self.select_question(chapter)
            if not question:
                print(f"No questions available in {chapter} or chapter is disabled.")
                break
                
            question_count += 1
            if self.ask_question(question):
                correct_count += 1
                
            print(f"\nProgress: {correct_count}/{question_count} ({int(correct_count/question_count*100) if question_count else 0}% correct)")
            
            choice = input("\nContinue with this chapter? (y/n): ").lower()
            if choice != 'y':
                break
        
        # Save weights back to the file
        self.save_quiz_data()

    def test_all_chapters(self):
        """Test all enabled chapters"""
        print("\n--- Testing All Enabled Chapters ---")
        
        enabled_chapters = [ch for ch in self.quiz_data.keys() if ch not in self.disabled_chapters]
        if not enabled_chapters:
            print("All chapters are disabled. Please enable at least one chapter.")
            return
            
        question_count = 0
        correct_count = 0
        
        # Create a list of questions from all enabled chapters
        all_questions = []
        for chapter in enabled_chapters:
            all_questions.extend([(chapter, q) for q in self.quiz_data[chapter]])
            
        # Shuffle questions
        random.shuffle(all_questions)
        
        for chapter, question in all_questions:
            print(f"\nChapter: {chapter}")
            question_count += 1
            if self.ask_question(question):
                correct_count += 1
                
            print(f"\nProgress: {correct_count}/{question_count} ({int(correct_count/question_count*100)}% correct)")
            
            if question_count % 5 == 0:  # Ask every 5 questions if they want to continue
                choice = input("\nContinue testing? (y/n): ").lower()
                if choice != 'y':
                    break
        
        print(f"\nFinal Score: {correct_count}/{question_count} ({int(correct_count/question_count*100) if question_count else 0}% correct)")
        
        # Save weights back to the file
        self.save_quiz_data()

    def show_statistics(self):
        """Show user performance statistics"""
        if not self.user_stats:
            print("\nNo statistics available yet.")
            return
            
        print("\n--- Your Statistics ---")
        
        for question, stats in self.user_stats.items():
            total = stats["correct"] + stats["incorrect"]
            if total > 0:
                accuracy = (stats["correct"] / total) * 100
                print(f"\nQuestion: {question[:60]}..." if len(question) > 60 else f"\nQuestion: {question}")
                print(f"Attempts: {total}, Correct: {stats['correct']}, Incorrect: {stats['incorrect']}")
                print(f"Accuracy: {accuracy:.1f}%")

    def run(self):
        """Run the quiz application"""
        print("Welcome to the Biology Quiz Study Program!")
        
        while True:
            print("\n--- Main Menu ---")
            print("1. List Chapters")
            print("2. Study a Chapter")
            print("3. Test All Chapters")
            print("4. Enable/Disable Chapters")
            print("5. Show Statistics")
            print("6. Exit")
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.list_chapters()
                
            elif choice == '2':
                self.list_chapters()
                try:
                    chapter_idx = int(input("\nEnter chapter number to study: "))
                    chapters = list(self.quiz_data.keys())
                    if 1 <= chapter_idx <= len(chapters):
                        chapter = chapters[chapter_idx - 1]
                        if chapter in self.disabled_chapters:
                            print(f"Chapter '{chapter}' is disabled. Please enable it first.")
                        else:
                            self.study_chapter(chapter)
                    else:
                        print("Invalid chapter number!")
                except ValueError:
                    print("Please enter a valid number")
                    
            elif choice == '3':
                self.test_all_chapters()
                
            elif choice == '4':
                self.list_chapters()
                try:
                    chapter_idx = int(input("\nEnter chapter number to toggle: "))
                    self.toggle_chapter(chapter_idx)
                except ValueError:
                    print("Please enter a valid number")
                    
            elif choice == '5':
                self.show_statistics()
                
            elif choice == '6':
                print("Thank you for using the Biology Quiz Study Program!")
                break
                
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Check if user wants to use a specific quiz file
    quiz_file = input("Enter quiz file path (or press Enter for default 'quiz_data.json'): ").strip()
    if not quiz_file:
        quiz_file = "quiz_data.json"
        
    quiz = BiologyQuiz(quiz_file)
    quiz.run()
