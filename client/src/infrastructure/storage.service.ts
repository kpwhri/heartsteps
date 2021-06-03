import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";


@Injectable()
export class StorageService {

    constructor(
        private storage: Storage
    ) {}

    public get(key:string):Promise<any> {
        return this.storage.get(key)
        .then((data:any) => {
            if(data === null) {
                return Promise.reject('Null');
            } else {
                return Promise.resolve(data);
            }
        });
    }

    public set(key:string, value:any):Promise<any> {
        return this.storage.set(key, value)
        .then(() => {
            return value;
        });
    }

    public remove(key:string):Promise<any> {
        return this.storage.remove(key);
    }

    public clear():Promise<any> {
        return this.storage.clear();
    }

    public keys(): Promise<string[]> {
        return this.storage.keys();
    }
}