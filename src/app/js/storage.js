class QuestionStorage {

  constructor() {
    this.prefix = 'hisquiz';    
  }

  load(key, def) {
    let value = localStorage.getItem(this.makeKey(key));
    return value ? JSON.parse(value) : def;
  }

  save(key, value) {
    localStorage.setItem(this.makeKey(key), JSON.stringify(value));
  }

  delete(key) {
    localStorage.removeItem(this.makeKey(key)); 
  }

  makeKey(key) {
    return this.prefix + '-' + key;
  }
	
}