from flask import abort, Flask, render_template, redirect, request, url_for
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap5

import settings
from forms import QuestionForm
from questions import Question, QuestionNotFound, Questions


def create_app():
    flask_app = Flask(__name__)
    flask_app.secret_key = settings.SECRET_KEY

    # set default button sytle and size, will be overwritten by macro parameters
    flask_app.config['BOOTSTRAP_BTN_STYLE'] = 'primary'

    bootstrap = Bootstrap5(flask_app)
    csrf = CSRFProtect(flask_app)

    @flask_app.route('/', methods=['GET'])
    def question_list():
        return render_template('question_list.html', questions=Questions.data().list())

    @flask_app.route('/add', methods=['GET', 'POST'])
    def question_add():
        form = QuestionForm()
        if form.validate_on_submit():
            question = Question.add_from_form(form)
            Questions.data().save(question, add=True)
            return redirect(url_for('question_list'))
        return render_template('question_edit.html', form=form, can_delete=False)

    @flask_app.route('/<question_id>/edit', methods=['GET', 'POST'])
    def question_edit(question_id):
        try:
            question = Questions.data().get(question_id)
            form = QuestionForm(
                chapter=question.chapter,
                route=question.route,
                image=question.image,
                question_number=question.question_number,
                title=question.title,
                answers='\n'.join(question.answers),
                answer=question.answer
            )
            if form.validate_on_submit():
                question = question.save_from_form(form)
                Questions.data().save(question)
                return redirect(url_for('question_list'))
            return render_template('question_edit.html', form=form, question=question, can_delete=True)
        except QuestionNotFound:
            abort(404)

    @flask_app.route('/<question_id>/delete', methods=['GET', 'POST'])
    def question_delete(question_id):
        try:
            question = Questions.data().get(question_id)
            if request.method == 'POST':
                Questions.data().delete(question)
                return redirect(url_for('question_list'))
            return render_template('question_delete.html', question=question)
        except QuestionNotFound:
            abort(404)

    return flask_app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
