import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { HeartstepsServer } from "../infrastructure/heartsteps-server.service";

const locationsKey = 'participant-locations'

@Injectable()
export class LocationsService{

    constructor(
        private heartstepsServer:HeartstepsServer,
        private storage:Storage
    ){}

    getLocations():Promise<any> {
        return this.storage.get(locationsKey)
        .then((locations) => {
            return locations
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    saveLocations(locations:any):Promise<Boolean> {
        return this.heartstepsServer.post('locations', {
            locations: locations
        })
        .then((locations) => {
            this.storage.set(locationsKey, locations)
        })
        .then(() => {
            return Promise.resolve(true)
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

}