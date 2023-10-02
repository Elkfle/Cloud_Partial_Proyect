// En tu archivo donde defines las instancias de axios (por ejemplo, axios.js o api.js)

import axios from "axios";
import store from "@/store/store.js"; // Ajusta la ruta según la ubicación de tu store

const userAPI = axios.create({
  baseURL: "lb-prod-proy-167809630.us-east-1.elb.amazonaws.com:8000/api", //5001
});

const gamesAPI = axios.create({
  baseURL: "lb-prod-proy-167809630.us-east-1.elb.amazonaws.com:8800/api", //5002
});

export { userAPI, gamesAPI };