class QuizManage {

  constructor(router, template, client) {
    this.router = router;
    this.template = template;
    this.client = client;
  }

  init() {
    this.setUpRoutes();
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
    this.router.on('/chapters', () => {
      self.editChapters();
    }); 
    this.router.on('/images', () => {
      self.editImages();
    });

  }

  listQuestions() {
    let self = this;

    this.client.getJson('/questions').then( (res) => {
      self.updateContent(self.template.render('question_list.html', {questions: res.json}));
      self.setUpPageNavigation();
    });
  }

  editQuestion(questionId) {
    let self = this;

    this.client.getJson('/questions/' + questionId).then( (res) => { 
      let question = res.json;
      self.loadChapters((chapters, images) => {
        self.updateContent(self.template.render('question_edit.html', {question: question, chapters: chapters, images: images}));
        self.setUpPageNavigation();
        document.getElementById('submit').addEventListener('click', (event) => {
          event.preventDefault();
          let form = document.getElementById('question-form');
          let formData = new FormData(form);
          let alertContainer = document.getElementById('alert-container');
          let alert = document.getElementById('alert');
          alertContainer.style.display = "none";
          self.client.putJson('/questions/' + questionId, self.buildQuestionJson(formData)).then( (res) => {
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
    
    this.loadChapters((chapters, images) => {
      self.updateContent(self.template.render('question_add.html', {chapters: chapters, images: images}));
      self.setUpPageNavigation();
      document.getElementById('submit').addEventListener('click', (event) => {
        event.preventDefault();
        let form = document.getElementById('question-form');
        let formData = new FormData(form);
        let alertContainer = document.getElementById('alert-container');
        let alert = document.getElementById('alert');
        alertContainer.style.display = "none";
        self.client.postJson('/questions', self.buildQuestionJson(formData)).then( (res) => {
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

    this.client.deleteJson('/questions/' + questionId).then( (res) => { 
      if (!res.ok) {
        alert(JSON.stringify(res.json));
      }
      else {
        self.router.navigate('/');
      }
    });
  }

  loadChapters(onSuccess) {
    let self = this;

    this.client.getJson('/chapters').then( (res) => {
      let chapters = res.json;
      self.client.getJson('/images').then( (res) => {
        let images = res.json;
        onSuccess(chapters, images);
      });
    });
  }

  saveChapters(formData, onSuccess, onFailure) {
    let self = this;

    let errors = [];
    this.client.putJson('/chapters', self.buildChaptersJson(formData)).then( (res) => {
      if (!res.ok) {
        errors.push(res.json);
        onFailure(errors);
      }
      else {
        onSuccess();
      }
    });

  }


  loadImages(onSuccess) {
    let self = this;

    this.client.getJson('/images').then( (res) => {
      let images = res.json;
      onSuccess(images);
    });
  }

  saveImages(formData, onSuccess, onFailure) {
    let self = this;

    let errors = [];
    this.client.put('/images', formData).then( (res) => {
      if (!res.ok) {
        errors.push(res.json);
        onFailure(errors);
      }
      else {
        onSuccess();
      }
    });

  }

  editChapters() {
    let self = this;
    
    this.loadChapters((chapters, images) => {
      self.updateContent(self.template.render('chapters_edit.html', {chapters: chapters, images: images}));
      self.setUpPageNavigation();
      self.setUpChaptersButtons(images);
      document.getElementById('submit').addEventListener('click', (event) => {
        event.preventDefault();
        let form = document.getElementById('chapters-form');
        let formData = new FormData(form);
        let alertContainer = document.getElementById('alert-container');
        let alert = document.getElementById('alert');
        alertContainer.style.display = "none";
        self.saveChapters(formData, () => self.router.navigate('/'), (errors) => {
          alert.innerHTML = JSON.stringify(errors);
          alertContainer.style.display = "block";
        });
      });
    });
  }

  editImages() {
    let self = this;
    
    this.loadImages((images) => {
      self.updateContent(self.template.render('images_edit.html', {images: images}));
      self.setUpPageNavigation();
      self.setUpImagesButtons();
      document.getElementById('submit').addEventListener('click', (event) => {
        event.preventDefault();
        let form = document.getElementById('images-form');
        let formData = new FormData(form);
        let alertContainer = document.getElementById('alert-container');
        let alert = document.getElementById('alert');
        alertContainer.style.display = "none";
        self.saveImages(formData, () => self.router.navigate('/'), (errors) => {
          alert.innerHTML = JSON.stringify(errors);
          alertContainer.style.display = "block";
        });
      });
    });
  }

  updateContent(text) {
    let content = document.getElementById('content');
    content.innerHTML = text;
  }

  buildQuestionJson(formData) {
    return {
        "answer": formData.get('answer'),
        "answered": null,
        "answers": formData.getAll('answers'),
        "chapter": formData.get('chapter'),
        "question_id": formData.get('question_id'),
        "question_number": formData.get('question_number'),
        "title": formData.get('title')
    };
  }

  buildChaptersJson(formData) {
    let chapters = [];
    let routes = formData.getAll('routes');
    let images = formData.getAll('images');
    formData.getAll('chapters').forEach( (chapter, index) => {
      chapters.push({
        chapter: chapter,
        route: routes[index],
        image: images[index]
      })
    });
    return {
        "chapters": chapters
    };
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

  setUpChaptersButtons(images) {
    let self = this;

    this.initRemoveChaptersButtons();
    
    document.getElementById('add-chapter').addEventListener('click', (event) => {
      let chapterCount = document.querySelectorAll('#chapter-container .input-group').length;
      let chapterContainer = document.getElementById('chapter-container');
      chapterContainer.insertAdjacentHTML('beforeend', self.template.render('chapter_field.html', {index: chapterCount + 1, images: images}));
      self.initRemoveChaptersButtons();
    });
  }

  initRemoveChaptersButtons() {
    document.querySelectorAll('.btn-danger').forEach( (el) => {
      el.addEventListener('click', (event) => {
        let chapterId = event.target.getAttribute('data-chapter');
        if (chapterId) {
          event.preventDefault();
          document.getElementById(chapterId).remove();
        }
      });
    });  
  }

  setUpImagesButtons() {
    let self = this;

    this.initRemoveImagesButtons();
    
    document.getElementById('add-image').addEventListener('click', (event) => {
      let imageCount = document.querySelectorAll('#image-container .input-group').length;
      let imageContainer = document.getElementById('image-container');
      imageContainer.insertAdjacentHTML('beforeend', self.template.render('image_field.html', {index: imageCount + 1}));
      self.initRemoveImagesButtons();
    });
  }

  initRemoveImagesButtons() {
    document.querySelectorAll('.btn-danger').forEach( (el) => {
      el.addEventListener('click', (event) => {
        let imageId = event.target.getAttribute('data-image');
        if (imageId) {
          event.preventDefault();
          document.getElementById(imageId).remove();
        }
      });
    });  
  }

}