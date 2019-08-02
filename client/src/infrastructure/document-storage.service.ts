import { Injectable } from "@angular/core";
import { StorageService } from "./storage.service";

export class DocumentStorage {

    private key:string;
    private storage:StorageService;

    constructor(key:string, storage:StorageService) {
        this.key = key;
        this.storage = storage;
    }

    public get(id:string):Promise<any> {
        return this.getData()
        .then((data) => {
            if(data[id] !== undefined) {
                return data[id];
            } else {
                return Promise.reject("Data not found");
            }
        });
    }

    public getAll():Promise<any> {
        return this.getData();
    }

    public getList():Promise<Array<any>> {
        return this.getData()
        .then((data) => {
            return Object.keys(data).map((key) => {
                return data[key];
            });
        });
    }

    public getIds():Promise<Array<string>> {
        return this.getData()
        .then((data) => {
            return Object.keys(data);
        });
    }

    public setAll(objects:any): Promise<boolean> {
        return this.setData(objects);
    }

    public setMany(objects:any):Promise<boolean> {
        return this.getAll()
        .then((data) => {
            Object.keys(objects).forEach((key) => {
                data[key] = objects[key];
            })
            return this.setData(data);
        })
        .then(() => {
            return true;
        });
    }

    public set(id:string, value:any):Promise<any> {
        return this.getData()
        .then((data) => {
            data[id] = value;
            return this.setData(data);
        })
        .then(() => {
            return value;
        });
    }

    public remove(id:string):Promise<boolean> {
        return this.getData()
        .then((data) => {
            delete data[id];
            return this.setData(data);
        })
        .then(() => {
            return true;
        })
    }

    public destroy():Promise<boolean> {
        return this.storage.remove(this.key);
    }

    private getData():Promise<any> {
        return this.storage.get(this.key)
        .then((data) => {
            return data;
        })
        .catch(() => {
            return {};
        });
    }

    private setData(data:any):Promise<any> {
        return this.storage.set(this.key, data);
    }
}

@Injectable()
export class DocumentStorageService {

    constructor(
        private storage: StorageService
    ) {}

    create(key:string):DocumentStorage {
        return new DocumentStorage(key, this.storage);
    }

}
