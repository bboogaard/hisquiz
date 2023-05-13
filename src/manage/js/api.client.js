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

  async request(method, path, data) {  
    const response = await fetch(this.apiUrl + path, {
      method: method,
      mode: "cors", // no-cors
      cache: "no-cache",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Basic " + btoa(this.username + ':' + this.password)
      },
      redirect: "follow",
      referrerPolicy: "no-referrer",
      body: data ? JSON.stringify(data) : null, // body data type must match "Content-Type" header
    }).then( async (res) => {
      try {
        const json = await res.json();
        return {
          ok: res.ok,
          json: json
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

}