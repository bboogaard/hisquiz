class ApiClient {

  constructor(apiUrl) {
  	this.apiUrl = apiUrl;
  }

  async get(path, data) {
    return this.request("GET", path, data);
  }

  async getJson(path, data) {
  	return this.request("GET", path, data, true);
  }

  async request(method, path, data, as_json) {   
    let headers = {
      "Authorization": "Basic " + btoa(this.username + ':' + this.password)
    }
    let query = data ? '?' + new URLSearchParams(data) : "";
    if (as_json) {
      headers["Content-Type"] = "application/json";
    }
    const response = await fetch(this.apiUrl + path + query, {
      method: method,
      mode: "cors", // no-cors
      cache: "no-cache",
      headers: headers,
      redirect: "follow",
      referrerPolicy: "no-referrer",
      body: null, // body data type must match "Content-Type" header
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