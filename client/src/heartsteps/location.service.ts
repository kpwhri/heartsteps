import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { Geolocation } from '@ionic-native/geolocation';

const locationPermissionKey = 'location-service-permission'

@Injectable()
export class LocationService{

    constructor(
        private geolocation:Geolocation,
        private storage:Storage
    ){}

    hasPermission():Promise<boolean> {
        return this.storage.get(locationPermissionKey)
        .then((value) => {
            if(value) {
                return Promise.resolve(true)
            } else {
                return Promise.reject(false)
            }
        }).catch(() => {
            return Promise.reject(false)
        })
    }

    getPermission():Promise<boolean> {
        return this.geolocation.getCurrentPosition()
        .then(() => {
            return this.storage.set(locationPermissionKey, true)
        })
        .then(() => {
            return Promise.resolve(true)
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

}