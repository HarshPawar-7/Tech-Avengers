from flask import Flask, render_template, request, redirect, send_from_directory, session, jsonify
import markdown
import os
import time
from datetime import datetime
from pytz import timezone
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'Lub_U'  # Replace with a secure random key

# Define answers and quotes
answers = [
    "STONES", 
    "Nidavellir",
    "4388722113523324618740564061945396299807387494243892209782120116862698769651520789601144473769074847359830104016205570082929893236827311214484101487547873069356997497404918033913164338595753059661933563510272153982126703907739486437102988024008330659142937251391425120000", 
    "(1010, 9980, 10079800, 9.88, 5744.5)", 
    "8304",
    "9981459.38",
    "50", 
    "The hardest choices require the Strongest Wills THANOS", 
      
    
]

quote_img = [
    ('\"A is A, but sometimes, A is G.\"', '1.webp'),
    ('\"Late late says the White Rabbit.\"', '2.jpeg'),
    ('Somewhere, Under a Starry Sky.', 'reality.png'),
    ('Old Home', 'soul.png'),
    ('The Leaning Tower of Babel', '5.jpg'),
    ('6.txt', '6.jpg'),
    ('...', '7.jpg'),
    ('Decretum', '8.jpg')
]



@app.route("/")
def index():
    session['current_question'] = 1  # Initialize the session with the first question
    session['questions_solved'] = 0   # Initialize questions solved counter
    session['start_time'] = time.time() # Track start time
    session['time_spent'] = []  # Track time spent on each question
    session['last_correct_time'] = None  # Track last correct answer time
    return render_template('index.html', question=session['current_question'])

@app.route("/chapter/<int:q_no>/")
def q(q_no):
    if 'current_question' not in session or q_no != session['current_question']:
        return redirect(f"/chapter/{session['current_question']}/", code=302)

    if q_no < 1 or q_no > 8:
        return redirect("/", code=302)

    array_index = q_no - 1
    questions_dir = 'questions'
    markdown_file_path = os.path.join(questions_dir, f'{q_no}.md')
    quote_ani_image = quote_img[array_index]
    question_content = "Question not found."

    if os.path.exists(markdown_file_path):
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            question_content = markdown.markdown(file.read())

    x = '/static/images/'
    y = '/input/'

    # Define stone colors
    stone_colors = {
        1: "#88141d",  
        2: "#263a4f",  
        3: "#002900",  # Time Stone (Green)
        4: "#410041",  # Power Stone (Purple)
        5: "#3b0000",  # Reality Stone (Red)
        6: "#815300",  # Soul Stone (Orange)
        7: "#000035",  # Space Stone (Blue)
        8: "#5f5f00",  # Mind Stone (Yellow)
        # 7: "#FFFFFF",  # Extra Question (White)
        9: "#808080"   # Final Question (Gray)
    }

    bg_color = stone_colors.get(q_no, "linear-gradient(270deg, rgba(86, 11, 36, 0.95), 30%, rgba(41, 14, 78, 0.95))")  # Default to black if not found

    print(f"Debug: Question {q_no}, Background Color: {bg_color}")  # Debugging line

    return render_template(
        'q.html',
        episode=q_no,
        question=question_content,
        form_link=q_no,
        input=y + quote_ani_image[0],
        image=x + quote_ani_image[1],
        bg_color=bg_color  # Pass bg_color to the template
    )


@app.route('/input/<filename>')
def input_file(filename):
    return send_from_directory('input', filename)

@app.route("/chapter/0/", methods=["GET"])
def redirect_internal():
    return redirect("/", code=302)



# Define your preferred timezone (change this if needed)
local_tz = timezone('Asia/Kolkata')

@app.route('/chapter/<int:q_no>/submit', methods=['POST'])
def check_ans(q_no):
    array_index = q_no - 1
    user_answer = request.form['answer'].strip()

    # Record the time spent on the current question
    end_time = time.time()
    time_spent = end_time - session['start_time']  # Time taken since the session started
    session['time_spent'].append(time_spent)  # Append time spent on the current question

    # Check the answer
    if user_answer.lower() == answers[array_index].lower():
        session['questions_solved'] += 1  # Increment the solved questions count

        # Get the current time in the desired timezone
        current_time = datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S")
        session['last_correct_time'] = current_time  # Record last correct answer time
        
        if array_index >= 7:
            return render_template('credits.html', questions_solved=session['questions_solved'], time_spent=session['time_spent'], last_correct_time=session['last_correct_time'])
        else:
            session['current_question'] = q_no + 1  # Move to the next question
            session['start_time'] = time.time()  # Reset the timer for the next question
            return render_template('result.html', ans_feedback='Congratulations, you have secured the Stone :)', q_no=q_no, question_pointer=int(q_no) + 1, link_msg='Continue your Search', result='correct')
    else:
        return render_template('result.html', ans_feedback='Oops! That is not the correct answer :(', q_no=q_no, question_pointer=int(q_no), link_msg='Try again', result='incorrect')

@app.route('/credits/')
def credits():
    end_time = time.time()
    total_time_taken = end_time - session['start_time']
    return render_template('credits.html', questions_solved=session['questions_solved'], time_spent=session['time_spent'], last_correct_time=session['last_correct_time'], total_time_taken=total_time_taken)

@app.route('/timer')
def timer():
    # Returns the remaining time in seconds
    remaining_time = 120 - (time.time() - session['start_time'])  # 120 minutes in seconds
    return jsonify({'remaining_time': remaining_time})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
