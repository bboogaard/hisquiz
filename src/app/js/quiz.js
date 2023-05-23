class Quiz {

  constructor(storage, router, client) {
    this.storage = storage;
    this.router = router;
    this.client = client;
    this.elements = {};
    this.currentQuestion = null;
    this.chapters = [];
    this.questions = [];
  }

  init() {
    let self = this;

    this.loadMeta( () => {
      self.setUpElements();
      self.setUpRoutes();
      self.setUpEventHandlers();
      self.loadAnswers();

      self.resumeQuiz();
      self.updateElements();

      self.router.resolve();
    });
  }

  // Methods for loading meta data

  loadMeta(onSuccess) {
    let self = this;

    this.client.getJson('/chapters').then( (res) => {
      self.chapters = res.json;
      self.client.getJson('/questions').then( (res) => {
        self.questions = res.json;
        onSuccess();
      });
    });
  }

  // Load saved data into prototype attributes or DOM elements

  loadAnswers() {
    let self = this;
    let savedQuestions = this.storage.load('questions', {});

    this.questions.forEach( (question) => {
      if (savedQuestions[question.questionId] !== undefined) {
        question.answered = savedQuestions[question.questionId];
      }
    });
  }

  resumeQuiz() {
    let self = this;

    let progress = this.sumAttr((question) => {
      return question.answered !== null;
    });
    if (progress === 0) {
      this.router.navigate('/');
    }
    else {
      let questionId = this.storage.load('questionId', null);
      if (questionId) {
        setTimeout( () => {
          this.findQuestion({questionId: questionId}, (question) => {
            self.loadQuestion(question);
          })
        }, 500);
      }
    }
  }

  // Update prototype attributes during the app cycle

  clearQuestions() {
    this.questions.forEach((question) => {
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
    let self = this;

    let question = this.getQuestion(this.currentQuestion.questionId);
    if (question) {
      question.answered = answered;
    }
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
        let query = self.currentQuestion !== null ? {questionId: self.currentQuestion.questionId} : {"chapter.chapter": chapter.chapter};
        self.findQuestion(query, (question) => {
          self.loadQuestion(question);
        })
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
      self.goToQuestion({"chapter.chapter": self.chapters[0].chapter}, () => {
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
      self.goToQuestion({questionId: self.currentQuestion.meta.prevQuestion});
    });
    this.elements.next.addEventListener("click", (event) => {
      self.goToQuestion({questionId: self.currentQuestion.meta.nextQuestion});
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
    let savedQuestions = {};

    this.questions.forEach( (question) => {
      savedQuestions[question.questionId] = question.answered;
    });
    this.storage.save('questions', savedQuestions);
  }

  deleteQuestions() {
    this.storage.delete('questions');
  }

  // Load the current question
    
  loadQuestion(question) {
    this.currentQuestion = question;
    this.toggleButton(this.elements.prev, this.currentQuestion.meta.prevQuestion !== null);
    this.toggleButton(this.elements.next, this.currentQuestion.meta.nextQuestion !== null);
    
    this.elements.chapterTitle.innerHTML = this.currentQuestion.chapter.chapter;
    this.elements.chapterImage.src = this.currentQuestion.chapter.image.url;
    this.elements.questionTitle.innerHTML = this.currentQuestion.questionNumber + ". " + this.currentQuestion.title;
    
    let labelIndex = 0;
    for (let label of this.elements.labels) {
      label.innerHTML = this.currentQuestion.answers[labelIndex++];
    }
    let answerIndex = 0;
    let answered = this.getAnswer(this.currentQuestion.questionId);
    for (let answer of this.elements.answers) {
      answer.checked = false;
      if (answered === answerIndex++) {
        answer.checked = true;
        break;
      }
    }
    this.toggleAnswers(answered === null);
    this.saveQuestion();
  }

  // Miscellaneous helpers

  getQuestion(questionId) {
    let self = this;

    let questions = this.questions.filter( (question) => {
      return question.questionId === questionId;
    });
    return questions.length ? questions[0] : null;
  }

  getAnswer(questionId) {
    let self = this;

    let question = this.getQuestion(questionId);
    return question ? question.answered : null;
  }
     

  findQuestion(query, onSuccess) {
    let self = this;

    this.client.getJson('/questions/find', query).then( (res) => {
      if (res.ok) {
        onSuccess(res.json);
      }
    });
  }

  goToQuestion(query, callback) {
    let self = this;

    this.findQuestion(query, (question) => {
      self.loadQuestion(question);
      self.router.navigate(self.currentQuestion.chapter.route);
      if (callback) {
        callback();
      }
    });
    
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
    this.questions.forEach( (question) => {
      if (condition(question)) {
        result += 1;
      }
    });
    return result;
  }

}