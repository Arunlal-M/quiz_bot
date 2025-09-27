
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")

    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)
        first_question, first_question_id = get_next_question(None)
        if first_question:
            bot_responses.append(first_question)
        session["current_question_id"] = first_question_id
        session.save()
        return bot_responses

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    if current_question_id is None:
        return True, ""
    
    if current_question_id < 0 or current_question_id >= len(PYTHON_QUESTION_LIST):
        return False, "No more questions"
    
    question = PYTHON_QUESTION_LIST[current_question_id]
    options = question.get('options', [])
    
    if not options:
        return True, ""
    
    answer_upper = answer.upper().strip()
    valid_letters = ['A', 'B', 'C', 'D'][:len(options)]
    
    if answer_upper not in valid_letters:
        return False, f"Please give A, B, C, or D as your answer."
    
    if 'answers' not in session:
        session['answers'] = {}
    
    option_index = ord(answer_upper) - 65
    session['answers'][str(current_question_id)] = options[option_index]
    return True, ""


def get_next_question(current_question_id):
    if current_question_id is None:
        next_id = 0
    else:
        next_id = current_question_id + 1
    
    if next_id >= len(PYTHON_QUESTION_LIST):
        return None, None
    
    question = PYTHON_QUESTION_LIST[next_id]
    question_text = question['question_text']
    options = question.get('options', [])
    
    result = question_text + "<br><br>"
    for i, option in enumerate(options):
        result += f"{chr(65+i)}. {option}<br>"
    
    return result, next_id


def generate_final_response(session):
    answers = session.get('answers', {})
    total = len(PYTHON_QUESTION_LIST)
    correct = 0
    
    for i in range(total):
        user_ans = answers.get(str(i), '')
        correct_ans = PYTHON_QUESTION_LIST[i].get('answer', '')
        
        if user_ans == correct_ans:
            correct += 1
    
    return f"You have Scored: {correct}/{total}"
