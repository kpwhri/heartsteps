import { Injectable } from "@angular/core";
import { Geolocation, Geoposition } from '@ionic-native/geolocation';
import { StorageService } from "./storage.service";

const locationPermissionKey = 'location-service-permission'

@Injectable()
export class LocationService{

    constructor(
        private geolocation:Geolocation,
        private storage:StorageService
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

    removePermission():Promise<boolean> {
        return this.storage.remove(locationPermissionKey);
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

    getLocation(): Promise<any> {
        return this.geolocation.getCurrentPosition()
        .then((position: Geoposition) => {
            return {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            }
        })
    }

}