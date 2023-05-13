class QuizManage {

  constructor(router, template, client) {
    this.router = router;
    this.template = template;
    this.client = client;
    this.elements = {};
    this.chapters = [];
    this.routes = [];
    this.images = [];
  }

  init() {
    this.setUpRoutes();

    this.listQuestions();
    this.router.resolve();
  }

  setUpRoutes() {
    let self = this;

    this.router.on('/', () => {
      self.listQuestions();
    });
    this.router.on(/([^/]+)\/edit$/, (match) => {
      self.editQuestion(match.data[0]);
    });
    this.router.on('/add', () => {
      self.addQuestion();
    });
    this.router.on(/([^/]+)\/delete$/, (match) => {
      self.deleteQuestion(match.data[0]);
    }); 

  }

  listQuestions() {
    let self = this;

    this.client.get('/questions').then( (res) => {
      self.updateContent(self.template.render('question_list.html', {questions: res.json}));
      self.setUpPageNavigation();
    });
  }

  editQuestion(questionId) {
    let self = this;

    this.client.get('/questions/' + questionId).then( (res) => { 
      let question = res.json;
      self.loadSettings(() => {
        self.updateContent(self.template.render('question_edit.html', {question: question, chapters: self.chapters, routes: self.routes, images: self.images}));
        self.setUpPageNavigation();
        document.getElementById('submit').addEventListener('click', (event) => {
          event.preventDefault();
          let form = document.getElementById('question-form');
          let formData = new FormData(form);
          let alertContainer = document.getElementById('alert-container');
          let alert = document.getElementById('alert');
          alertContainer.style.display = "none";
          self.client.put('/questions/' + questionId, self.buildJson(formData)).then( (res) => {
            if (!res.ok) {
              alert.innerHTML = JSON.stringify(res.json);
              alertContainer.style.display = "block";
            }
            else {
              self.router.navigate('/');
            }
          });
        });
      });
    });
  }

  addQuestion() {
    let self = this;
    
    this.loadSettings(() => {
      self.updateContent(self.template.render('question_add.html', {chapters: self.chapters, routes: self.routes, images: self.images}));
      self.setUpPageNavigation();
      document.getElementById('submit').addEventListener('click', (event) => {
        event.preventDefault();
        let form = document.getElementById('question-form');
        let formData = new FormData(form);
        let alertContainer = document.getElementById('alert-container');
        let alert = document.getElementById('alert');
        alertContainer.style.display = "none";
        self.client.post('/questions', self.buildJson(formData)).then( (res) => {
          if (!res.ok) {
            alert.innerHTML = JSON.stringify(res.json);
            alertContainer.style.display = "block";
          }
          else {
            self.router.navigate('/');
          }
        });
      });
    });
  }

  deleteQuestion(questionId) {
    let self = this;

    this.client.delete('/questions/' + questionId).then( (res) => { 
      if (!res.ok) {
        alert(JSON.stringify(res.json));
      }
      else {
        self.router.navigate('/');
      }
    });
  }

  loadSettings(onSuccess) {
    let self = this;

    this.client.get('/chapters').then( (res) => {
      self.chapters = res.json;
      self.client.get('/routes').then( (res) => {
        self.routes = res.json;
        self.client.get('/images').then( (res) => {
          self.images = res.json;
          onSuccess();
        });
      });
    });
  }

  updateContent(text) {
    let content = document.getElementById('content');
    content.innerHTML = text;
  }

  buildJson(formData) {
    return JSON.stringify({
        "answer": formData.get('answer'),
        "answered": null,
        "answers": formData.getAll('answers'),
        "chapter": formData.get('chapter'),
        "image": formData.get('image'),
        "question_id": formData.get('question_id'),
        "question_number": formData.get('question_number'),
        "route": formData.get('route'),
        "title": formData.get('title')
    });
  }

  setUpPageNavigation() {
    let self = this;

    document.querySelectorAll('a').forEach( (el) => {
      el.addEventListener('click', (event) => {
        let href = event.target.getAttribute('href');
        if (href) {
          event.preventDefault();
          self.router.navigate(href);
        }
      });  
    });
  }

}