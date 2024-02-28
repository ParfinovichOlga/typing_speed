import pandas
import random
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showinfo

original_data = pandas.read_csv('words.csv')
data = original_data['word'].to_list()

with open('results.txt') as file:
    results = file.readlines()

FONT_NAME = "Courier 12"
MAX_WPM = int(results[0])
MAX_CPM = int(results[1])

correct_words = []
correct_symbols = []
start = 0
end = 0
# w - word's number in list correct_words
w = 0
# n - current word's symbol number
n = 0
timer = None
TIME = 60


def reset_game():
    global timer, w, n, start, end, data, correct_words, correct_symbols
    text.config(state='normal')
    random.shuffle(data)
    if timer is not None:
        window.after_cancel(timer)
        timer = None

    entry.config(state='normal')
    entry.delete(0, END)
    w = 0
    n = 0
    start = 0
    end = 0
    count_down(TIME)
    correct_words = []
    correct_symbols = []
    for tag in text.tag_names():
        text.tag_remove(tag, 1.0, END)
    canvas.itemconfig(score_words, text=f'WPM: ?')
    canvas.itemconfig(score_letters, text=f'CPM: ?')
    canvas.itemconfig(time, text='time: 60')

    text.insert(1.0, data)
    text.config(state='disabled')
    entry.focus_set()


# Change MAX_CPM, MAX_WPM in case restart
def change_constant(new_cpm, new_wpm):
    global MAX_CPM, MAX_WPM
    MAX_CPM = new_cpm
    MAX_WPM = new_wpm


# Set timer
def count_down(count):
    canvas.itemconfig(time, text=f'time: {count}')
    if count > 0:
        global timer
        timer = window.after(1000, count_down, count-1)
    else:
        entry.delete(0, END)
        entry.config(state='readonly')
        cpm = len(correct_symbols)
        wpm = count_wpm()
        canvas.itemconfig(score_letters, text=f'CPM: {cpm}')
        canvas.itemconfig(score_words, text=f'WPM: {wpm}')
        if wpm > MAX_WPM and cpm > MAX_CPM:
            with open('results.txt', mode='w') as fl:
                fl.write(f'{wpm}\n{cpm}')
            showinfo('Result', message=f'Congratulations! \n💪Best result: CPM - {cpm}, WPM - {wpm}\n'
                                       f'          VS\nprevious {MAX_CPM} CPM, {MAX_WPM} WPM')
            change_constant(cpm, wpm)

        else:
            showinfo('Result', message=f'Your score: {cpm} CPM, {wpm} WPM.\n\nYour best result was: CPM -'
                                       f' {MAX_CPM}, WPM - {MAX_WPM}')


# Change font color of correctly written word on blue
def right_word(start_index, end_index):
    text.tag_add('r', f'1.{start_index}', f'1.{end_index}')
    text.tag_config('r', foreground='blue')


# Change font color of wrong written word on red
def wrong_word(start_index, end_index):
    text.tag_add('w', f'1.{start_index}', f'1.{end_index}')
    text.tag_config('w', foreground='red')


# Highlight next wort to be written
def highlight():
    global end
    start_index = end
    end_index = start_index + len(data[w])
    text.tag_add('h', f'1.{start_index}', f'1.{end_index}')
    text.tag_config('h', background='light green')


# Highlight wrong symbol with orange
def wrong_symbol(s, e):
    text.tag_remove('h', 1.0, END)
    text.tag_add('h', f'1.{s}', f'1.{e}')
    text.tag_config('h', background='orange')


# Form list of correctly written words, move through the data
def shift_index(event):
    global w, n, correct_words, start, end
    user_input = entry.get().replace(' ', '')
    if user_input is not "":
        start = end
        end = start + int(len(data[w])) + 1

        if user_input == data[w]:
            correct_words.append(user_input)
            right_word(start, end)
        else:
            wrong_word(start, end)

        w += 1
        n = 0
        text.tag_remove('h', 1.0, END)
        highlight()
        entry.delete(0, END)


def count_wpm():
    letters = 0
    for word in correct_words:
        letters += len(word)
    return round(letters/5)


# Check symbol input
def check_input(event):
    global n, correct_symbols, start
    symbol_input = event.keysym
    letters_number = len(data[w]) - 1

    if symbol_input == data[w][n]:
        correct_symbols.append(symbol_input)
        if n < letters_number:
            n += 1
    elif len(symbol_input) > 1:
        if n > 0:
            n -= 1
    else:
        wrong_symbol(end + n, end + n + 1)
        if n < letters_number:
            n += 1


window = Tk()
window.title("Check your typing speed")
window.config(padx=50, pady=30, background='#DABDAB')

canvas = Canvas(width=650, height=256, highlightthickness=0, background='#DABDAB')
canvas.grid(column=0, row=0, columnspan=2)
score_words = canvas.create_text(40, 120)
score_letters = canvas.create_text(180, 120)
time = canvas.create_text(400, 120)

text = ScrolledText(wrap='word', relief='groove', height=6, spacing2=18, spacing1=7, font=FONT_NAME)
text.insert(1.0, data)
text.config(state='disabled')
text.grid(column=0, row=1, columnspan=10)

start = Button(text='start', command=reset_game, width=15, bg='#BDECB6', relief='ridge')
start.grid(column=8, row=0)

entry = Entry(width=82, state='readonly', font=FONT_NAME)
entry.grid(column=0, row=10, columnspan=10, pady=50)
entry.bind('<space>', shift_index)
entry.bind('<Key>', check_input)

window.mainloop()