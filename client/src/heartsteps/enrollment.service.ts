import axios from 'axios'

export class EnrollmentService {
    
    constructor() {}

    enroll(enrollment_token:String) {
        return axios.post("http://localhost:8080/enroll",{
            enrollment_token: enrollment_token
        })
        .then((response) => {
            console.log(response);
            return true;
        })
        .catch((error) => {
            console.log(error);
            return false;
        })
    }
}