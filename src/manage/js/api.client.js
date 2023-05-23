class ApiClient {

  constructor(apiUrl) {
  	this.apiUrl = apiUrl;
  }

  login(username, password) {
    this.username = username;
    this.password = password;
  }

  async get(path) {
    return this.request("GET", path);
  }

  async post(path, data) {
    return this.request("POST", path, data);
  }

  async put(path, data) {
    return this.request("PUT", path, data);
  }

  async delete(path) {
    return this.request("DELETE", path);
  }

  async getJson(path) {
  	return this.request("GET", path, null, true);
  }

  async postJson(path, data) {
    return this.request("POST", path, data, true);
  }

  async putJson(path, data) {
    return this.request("PUT", path, data, true);
  }

  async deleteJson(path) {
    return this.request("DELETE", path, null, true);
  }

  async request(method, path, data, as_json) {   
    let headers = {
      "Authorization": "Basic " + btoa(this.username + ':' + this.password)
    }
    if (as_json) {
      headers["Content-Type"] = "application/json";
    }
    const response = await fetch(this.apiUrl + path, {
      method: method,
      mode: "cors", // no-cors
      cache: "no-cache",
      headers: headers,
      redirect: "follow",
      referrerPolicy: "no-referrer",
      body: data ? (as_json ? JSON.stringify(this.toCamelKeys(data)) : data) : null, // body data type must match "Content-Type" header
    }).then( async (res) => {
      try {
        const json = await res.json();
        return {
          ok: res.ok,
          json: this.toSnakeKeys(json)
        };
      }
      catch(error) {
        const json = {};
        return {
          ok: res.ok,
          json: json
        };
      }
    });
    return response;
  }

  toCamelKeys(data) {
    if (Array.isArray(data)) {
      let result = [];
      for (const obj of data) {
        result.push(this.toCamelKeys(obj));
      }
      return result;
    }
    else if (typeof data === 'object') {
      let result = {};
      for (const key in data) {
        result[this.toCamelCase(key)] = data[key];
      }
      return result;
    }
    else {
      return data;
    }
  }

  toSnakeKeys(data) {
    if (Array.isArray(data)) {
      let result = [];
      for (const obj of data) {
        result.push(this.toSnakeKeys(obj));
      }
      return result;
    }
    else if (typeof data === 'object') {
      let result = {};
      for (const key in data) {
        result[this.toSnakeCase(key)] = data[key];
      }
      return result;
    }
    else {
      return data;
    }
  }

  toCamelCase(str) {
    return str.toLowerCase().replace(/(_\w)/g, x => x.toUpperCase().substr(1));
  }

  toSnakeCase(str) {
    return str
    .match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g)
    .map(x => x.toLowerCase())
    .join('_');
  }
  

}