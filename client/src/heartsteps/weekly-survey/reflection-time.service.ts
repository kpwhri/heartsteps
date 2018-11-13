import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";

const storageKey = 'weeklyReflectionTime'

@Injectable()
export class ReflectionTimeService{

    constructor(
        private heartstepsServer:HeartstepsServer,
        private storage:Storage
    ){}

    getTime():Promise<any> {
        return this.storage.get(storageKey)
        .then((data) => {
            if(data) {
                return data;
            } else {
                return Promise.reject(false);
            }
        })
        .catch(() => {
            return Promise.reject(false);
        })
    }

    setTime(data:any):Promise<boolean> {
        return this.heartstepsServer.post('reflection-time', data)
        .then(() => {
            return this.storage.set(storageKey, data);
        })
        .then(() => {
            return true;
        })
    }

}