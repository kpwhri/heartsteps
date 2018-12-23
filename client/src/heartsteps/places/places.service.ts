import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { StorageService } from "@infrastructure/storage.service";

const locationsKey = 'participant-locations'

@Injectable()
export class PlacesService{

    constructor(
        private heartstepsServer:HeartstepsServer,
        private storage:StorageService
    ){}

    getLocations():Promise<any> {
        return this.storage.get(locationsKey)
        .then((locations) => {
            if(locations) {
                return locations
            } else {
                return Promise.reject(false)
            }
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    set(locations):Promise<any> {
        return this.storage.set(locationsKey, locations);
    }

    remove():Promise<boolean> {
        return this.storage.remove(locationsKey);
    }

    load():Promise<any> {
        return this.heartstepsServer.get('places')
        .then((places) => {
            return this.set(places);
        })
        .then((places) => {
            return places;
        })
    }

    validate(locations:any):Promise<boolean> {
        if(locations.length < 1) {
            return Promise.reject({message:"There must be at least one location"})
        }

        let atLeastOneHome = false
        locations.forEach((location) => {
            if(location.type === 'home') {
                atLeastOneHome = true
            }
        })
        if(!atLeastOneHome) {
            return Promise.reject({message: "At least one location must be a home location"})
        }

        let locationsIncomplete = false
        locations.forEach((location) => {
            if(!location.address || !location.latitude || !location.longitude) {
                locationsIncomplete = true
                location.invalid = true
            }
        })
        if(locationsIncomplete) {
            return Promise.reject({
                message: "All locations must be valid",
                locations: locations
            })
        }

        return Promise.resolve(true)
    }

    saveLocations(locations:any):Promise<Boolean> {
        return this.heartstepsServer.post('places', locations)
        .then((locations) => {
            return this.set(locations)
        })
        .then(() => {
            return Promise.resolve(true)
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

}