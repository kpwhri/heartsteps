import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Storage } from "@ionic/storage";

const storageKey = 'contact-information'

@Injectable()
export class ContactInformationService {

    constructor(
        private heartstepsServer:HeartstepsServer,
        private storage:Storage
    ){}

    get():Promise<any> {
        return this.storage.get(storageKey)
        .then((data) => {
            if (data) {
                return data
            } else {
                return Promise.reject()
            }
        })
        .catch(() => {
            return Promise.reject()
        })
    }

    getFromServer():Promise<any> {
        return this.heartstepsServer.get('contact-information')
        .then((data) => {
            return this.storage.set(storageKey, data)
            .then(() => {
                return data
            })
        })
    }

    save(contactInformation):Promise<boolean> {
        return this.heartstepsServer.post('contact-information', contactInformation)
        .then(() => {
            return this.storage.set(storageKey, contactInformation)
        })
        .then(()=>{
            return true
        })
        .catch(() => {
            return Promise.reject({
                'message': 'Something went wrong'
            })
        })
    }

}