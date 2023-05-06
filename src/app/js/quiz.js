class Quiz {

  constructor(questions, storage, router) {
    this.questions = questions;
    this.storage = storage;
    this.router = router;
    this.elements = {};
    this.currentQuestion = null;
    this.chapters = [];
  }

  init() {
    this.normalizeChapters();
    this.normalizeQuestions();
    this.loadAnswers();

    this.setUpElements();
    this.setUpRoutes();
    this.setUpEventHandlers();

    this.resumeQuiz();
    this.updateElements();

    this.router.resolve();
  }

  // Methods for normalizing data

  normalizeChapters() {
    let chapters = {}
    this.questions.forEach((question, i) => {
      if (chapters[question.route] === undefined) {
        chapters[question.route] = {
          chapter: question.chapter,
          questions: []
        }
      }
      chapters[question.route].questions.push(question.questionId);
    });
    this.chapters = [];
    for (const route in chapters) {
      let chapter = chapters[route];
      chapter.route = route;
      this.chapters.push(chapter);
    }
  }

  normalizeQuestions() {
    this.questions.forEach((question, i) => {
      question.questionIndex = i;
    });
  }

  // Load saved data into prototype attributes or DOM elements

  loadAnswers() {
    let self = this;

    let savedQuestions = this.storage.load('questions', []);  
    savedQuestions.forEach((savedQuestion, i) => {
      let question = self.findQuestion(savedQuestion.questionId);
      if (question !== null) {
        question.answered = savedQuestion.answered;
      }
    });
  }

  resumeQuiz() {
    let progress = this.sumAttr((question) => {
      return question.answered !== null;
    });
    if (progress === 0) {
      this.router.navigate('/');
    }
    else {
      let questionId = this.storage.load('questionId', null);
      this.currentQuestion = questionId ? this.findQuestion(questionId) : null;
      if (this.currentQuestion !== null) {
        this.router.navigate(this.currentQuestion.route);
      }
    }
  }

  // Update prototype attributes during the app cycle

  clearQuestions() {
    this.questions.forEach((question, i) => {
      question.answered = null;
    });
    this.deleteQuestions();
  }

  clearAnswers() {
    for (let answer of this.elements.answers) {
      answer.checked = false;
    }
  }

  saveAnswer(answered) {
    this.currentQuestion.answered = answered;
    this.toggleAnswers(false);
  }

  // Set up shortcuts to/Update DOM elements

  setUpElements() {
    this.elements = {
      start: document.getElementById('start'),
      goto: document.getElementById('goto'),
      gotoList: document.getElementById('goto-list'),
      stop: document.getElementById('stop'),
      chapterTitle: document.getElementById('chapter-title'),
      chapterImage: document.getElementById('chapter-image'),
      quizForm: document.getElementById('quiz-form'),
      quizIntro: document.getElementById('quiz-intro'),
      questionCount: document.getElementById('question-count'),
      chapterCount: document.getElementById('chapter-count'),
      questionTitle: document.getElementById('question-title'),
      labels: document.querySelectorAll(".form-check-label"),
      answers: document.querySelectorAll('input[name="answer"]'),
      prev: document.getElementById('prev'),
      next: document.getElementById('next'),
      progress: document.getElementById('progress'),
      score: document.getElementById('score')
    }
    this.elements.questionCount.innerHTML = this.questions.length;
    this.elements.chapterCount.innerHTML = this.chapters.length;
    for (let chapter of this.chapters) {
        let li = document.createElement('li');
        li.innerHTML = '<a href="' + chapter.route + '" class="dropdown-item">' + chapter.chapter + '</a>';
        this.elements.gotoList.appendChild(li);
    }
    this.elements.gotoLinks = document.querySelectorAll("#goto-list .dropdown-item");
  }

  // Set up routing

  setUpRoutes() {
    let self = this;

    this.chapters.forEach((chapter) => {
      self.router.on(chapter.route, () => {
        let question = self.currentQuestion !== null ? self.currentQuestion : self.findQuestion(chapter.questions[0]);
        if (question !== null) {
            self.loadQuestion(question.questionIndex);
        }
      }); 
    });
  }

  // Set up event handlers

  setUpEventHandlers() {
    let self = this;

    for (let answer of this.elements.answers) {
      answer.addEventListener("click", (event) => {
        let answered = parseInt(event.target.value, 10);
        self.saveAnswer(answered);
        self.saveQuestions();
        self.updateElements();
      });
    }
    this.elements.start.addEventListener("click", (event) => {
      event.preventDefault();
      self.goToQuestion(0, () => {
        self.toggleForm(true);
        self.toggleNav(self.elements.start, false, true);
      });
    });
    for (let gotoLink of this.elements.gotoLinks) {
      gotoLink.addEventListener("click", (event) => {
        event.preventDefault();
        self.currentQuestion = null;
        self.router.navigate(event.target.getAttribute('href'));
      });
    }
    this.elements.stop.addEventListener("click", (event) => {
      event.preventDefault();
      self.clearQuestions();
      self.clearAnswers();
      self.updateElements();
      self.router.navigate('/');
    });
    this.elements.prev.addEventListener("click", (event) => {
      self.goToQuestion(self.currentQuestion.questionIndex - 1);
    });
    this.elements.next.addEventListener("click", (event) => {
      self.goToQuestion(self.currentQuestion.questionIndex + 1);
    });
  }

  // Update DOM elements during the app cycle

  updateElements() {
    let progress = this.sumAttr((question) => {
      return question.answered !== null;
    });
    let score = this.sumAttr((question) => {
      return question.answered === question.answer;
    });

    if (progress === 0) {
      this.toggleNav(this.elements.start, true, true);
      this.toggleNav(this.elements.goto, false, false);
      this.toggleNav(this.elements.stop, false, true);
      this.toggleForm(false);
      this.toggleChapter(false);
    }
    else {
      this.toggleNav(this.elements.start, false, true);
      this.toggleNav(this.elements.goto, true, false);
      this.toggleNav(this.elements.stop, true, true);
      this.toggleForm(true);
    }
    
    let progressPerc = Math.round((progress / this.questions.length) * 100);
    this.elements.progress.setAttribute('style', 'width:' + progressPerc + '%');
    this.elements.progress.innerHTML = progressPerc + '%';
    let scorePerc = Math.round((score / this.questions.length) * 100);
    this.elements.score.setAttribute('style', 'width:' + scorePerc + '%');
    this.elements.score.innerHTML = scorePerc + '%';
  }

  // Save prototype attributes to local storage

  saveQuestion() {
    this.storage.save('questionId', this.currentQuestion.questionId);
  }

  saveQuestions() {
    this.storage.save('questions', this.questions.map((question, i) => {
      return {
        questionId: question.questionId,
        answered: question.answered
      }
    }));
  }

  deleteQuestions() {
    this.storage.delete('questions');
  }

  // Load the current question
    
  loadQuestion(questionIndex) {
    this.currentQuestion = this.questions[questionIndex];
    this.toggleButton(this.elements.prev, this.currentQuestion.questionIndex > 0);
    this.toggleButton(this.elements.next, this.currentQuestion.questionIndex < this.questions.length - 1);
    
    this.elements.chapterTitle.innerHTML = this.currentQuestion.chapter;
    this.elements.chapterImage.src = "images/" + this.currentQuestion.image;
    this.elements.questionTitle.innerHTML = this.currentQuestion.questionNumber + ". " + this.currentQuestion.title;
    
    let labelIndex = 0;
    for (let label of this.elements.labels) {
      label.innerHTML = this.currentQuestion.answers[labelIndex++];
    }
    let answerIndex = 0;
    for (let answer of this.elements.answers) {
      answer.checked = false;
      if (this.currentQuestion.answered === answerIndex++) {
        answer.checked = true;
        break;
      }
    }
    this.toggleAnswers(this.currentQuestion.answered === null);
    this.saveQuestion();
  }

  // Miscellaneous helpers
     

  findQuestion(questionId) {
    for (let question of this.questions) {
      if (question.questionId === questionId) {
        return question;
      }
    }
    return null;
  }

  goToQuestion(questionIndex, callback) {
    this.loadQuestion(questionIndex);
    this.router.navigate(this.currentQuestion.route);
    if (callback) {
      callback();
    }
  }


  toggleNav(element, state, toggleActive) {
    if (!state) {
      element.setAttribute('disabled', 'disabled');
      element.classList.add('disabled');
      if (toggleActive) {
        element.classList.remove('active');
      }
    }
    else {
      element.removeAttribute('disabled');
      element.classList.remove('disabled');
      if (toggleActive) {
        element.classList.add('active');
      }
    }
  }

  toggleForm(state) {
    if (!state) {
      this.elements.quizForm.style.display = "none";
      this.elements.quizIntro.style.display = "block";
    }
    else {
      this.elements.quizForm.style.display = "block";
      this.elements.quizIntro.style.display = "none";
    }
  }

  toggleChapter(state) {
    if (!state) {
      this.elements.chapterTitle.innerHTML = "HisQuiz";
      this.elements.chapterImage.src = "images/synode.png";
    }
  }

  toggleAnswers(state) {
    for (let answer of this.elements.answers) {
      if (!state) {
        answer.setAttribute('disabled', 'disabled');
      }
      else {
        answer.removeAttribute('disabled');
      }
    }
  }

  toggleButton(element, state) {
    if (!state) {
      element.setAttribute('disabled', 'disabled');
    }
    else {
      element.removeAttribute('disabled');
    }
  }

  sumAttr(condition) {
    let result = 0;
    this.questions.forEach((question, i) => {
      if (condition(question)) {
        result += 1;
      }
    });
    return result;
  }

}