
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    # Initialize current_question_id if not set
    current_question_id = session.get("current_question_id")
    if current_question_id is None:
        current_question_id = 0  # Start with the first question
        session["current_question_id"] = current_question_id
        session.save()
        bot_responses.append(BOT_WELCOME_MESSAGE)
        bot_responses.append(PYTHON_QUESTION_LIST[current_question_id]["question_text"])
        options = PYTHON_QUESTION_LIST[current_question_id]["options"]
        bot_responses.append(f"Options: {', '.join(options)}")
        return bot_responses

    # Process the user's response
    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    # Get the next question
    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
        options = PYTHON_QUESTION_LIST[next_question_id]["options"]
        bot_responses.append(f"Options: {', '.join(options)}")
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    # Update the session with the next question ID
    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    try:
        if "answers" not in session:
            session["answers"] = {}

        # Store the user's answer
        session["answers"][current_question_id] = answer
        session.save()
        return True, ""
    except Exception as e:
        return False, f"An error occurred while saving the answer: {str(e)}"
    # return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id + 1 < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[current_question_id + 1]["question_text"]
        next_question_id = current_question_id + 1
        return next_question, next_question_id
    else:
        # No more questions
        return None, -1


def generate_final_response(session):
    """
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    """
    answers = session.get("answers", {})
    score = 0

    for question_id, user_answer in answers.items():
        try:
            question_id = int(question_id)
            correct_answer = PYTHON_QUESTION_LIST[question_id]["answer"]
            if user_answer.strip().lower() == correct_answer.strip().lower():
                score += 1
        except (ValueError, IndexError, KeyError):
            # Log or handle invalid question_id
            continue

    total_questions = len(PYTHON_QUESTION_LIST)
    return f"You've completed the quiz! Your score is {score}/{total_questions}. Well done!"
