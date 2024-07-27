import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the Google Generative AI API
api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
genai.configure(api_key=api_key)

def initialize_session_state():
    if 'quiz' not in st.session_state:
        st.session_state.quiz = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'player_score' not in st.session_state:
        st.session_state.player_score = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'quiz_finished' not in st.session_state:
        st.session_state.quiz_finished = False
    if 'submitted_answer' not in st.session_state:
        st.session_state.submitted_answer = None

initialize_session_state()

def generate_quiz(topic, num_questions):
    prompt = (f"Create a multiple-choice quiz on the topic '{topic}'. "
              f"Provide {num_questions} questions with 4 options each and indicate the correct answer. "
              f"Format: Question\nOption A\nOption B\nOption C\nOption D\nCorrect Answer: Option")

    try:
        response = genai.generate_text(
            model='models/text-bison-001',  # Use the correct model name
            prompt=prompt,
            temperature=0.7,
            max_output_tokens=1500  # Adjust as needed
        )

        # Debug: Print the raw response
        st.write("Raw Response:", response.result)

        questions_text = response.result.strip().split("\n\n")
        quiz = []
        for q in questions_text:
            parts = q.split("\n")
            if len(parts) >= 6:  # Ensure there are enough parts for question, options, and correct answer
                question_text = parts[0].strip()
                options = [opt.strip() for opt in parts[1:5]]
                correct_answer = parts[5].split(": ")[1].strip()
                quiz.append({
                    "question": question_text,
                    "options": options,
                    "correct_answer": correct_answer
                })
            else:
                # Skip malformed questions without printing warnings
                continue
        return quiz

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

def display_question(question_data):
    st.write(f"### {question_data['question']}")
    options = question_data['options']
    selected_option = st.radio("Choose an answer:", options, key=f"question_{st.session_state.current_question}")
    return selected_option

def aimcq():
    st.title("AI-Generated MCQ Quiz")

    if not st.session_state.quiz_finished:
        topic = st.text_input("Enter Quiz Topic")
        num_questions = st.number_input("Set Number of Questions", min_value=1, max_value=100, step=1)

        if st.button("Generate Quiz"):
            st.session_state.quiz = generate_quiz(topic, num_questions)
            st.session_state.current_question = 0
            st.session_state.player_score = 0
            st.session_state.user_answers = []
            st.session_state.quiz_finished = False
            st.session_state.submitted_answer = None

        if st.session_state.quiz:
            current_q = st.session_state.current_question
            question_data = st.session_state.quiz[current_q]
            selected_answer = display_question(question_data)

            if st.button("Save and Next"):
                if selected_answer:
                    st.session_state.submitted_answer = selected_answer
                    st.session_state.user_answers.append(selected_answer)
                    if selected_answer == question_data['correct_answer']:
                        st.session_state.player_score += 1
                        st.write("**Correct!**")
                    else:
                        st.write(f"**The correct answer is: {question_data['correct_answer']}**")

                    # Move to the next question or end the quiz
                    if st.session_state.current_question < len(st.session_state.quiz) - 1:
                        st.session_state.current_question += 1
                    else:
                        st.session_state.quiz_finished = True

    else:
        st.write("### Quiz Completed!")
        st.write(f"### Your score is: **{st.session_state.player_score}/{len(st.session_state.quiz)}**")

        if st.session_state.player_score == len(st.session_state.quiz):
            st.write("### Congratulations! You scored a perfect score!")

        st.write("### Review your answers:")
        for i, q in enumerate(st.session_state.quiz):
            st.write(f"**Q{i+1}: {q['question']}**")
            st.write(f"Your answer: {st.session_state.user_answers[i]}")
            st.write(f"Correct answer: {q['correct_answer']}")

        if st.button("Scorecard"):
            st.write("### Detailed Scorecard")
            st.write(f"Your score: **{st.session_state.player_score}/{len(st.session_state.quiz)}**")
            st.write("### Review your answers:")
            for i, q in enumerate(st.session_state.quiz):
                st.write(f"**Q{i+1}: {q['question']}**")
                st.write(f"Your answer: {st.session_state.user_answers[i]}")
                st.write(f"Correct answer: {q['correct_answer']}")

        if st.button("Return Home"):
            st.session_state.quiz_finished = False
            st.session_state.current_question = 0
            st.session_state.player_score = 0
            st.session_state.user_answers = []
            st.write("You have been returned to the home screen. You can generate a new quiz.")

aimcq()
