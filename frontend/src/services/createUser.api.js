import axios from "axios";
import { userAPI } from "@/utils/axios.js"

export default {
    async registerUser(username, password, email, age){
        try {
            const response = await userAPI.post("register", { username, password, email, age });
            return response.data;
        } catch(err) {
            console.log(err);
            throw err; 
        }
    }
};