import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { Subject } from "rxjs/Subject";
import { Observable } from "rxjs/Observable";
import { HeartstepsNotifications } from "./heartsteps-notifications.service";
import { ActivitySuggestionTimeService } from "./activity-suggestion-time.service";
import { LocationService as GeolocationService } from "@infrastructure/location.service";
import { PlacesService } from "@heartsteps/places.service";
import { ContactInformationService } from "@heartsteps/contact-information.service";
import { ReflectionTimeService } from "@heartsteps/reflection-time.service";

const storageKey = 'heartsteps-id'

@Injectable()
export class ParticipantService {

    private subject:Subject<any>;

    constructor(
        private storage:Storage,
        private notificationService:HeartstepsNotifications,
        private activitySuggestionTimeService:ActivitySuggestionTimeService,
        private geolocationService:GeolocationService,
        private placesService:PlacesService,
        private contactInformationService: ContactInformationService,
        private reflectionTimeService: ReflectionTimeService
    ) {
        this.subject = new Subject();
    }

    hasCompleteProfile():Promise<boolean> {
        return this.getProfile()
        .then((profile) => {
            let complete = true
            Object.keys(profile).forEach((key) => {
                if(!profile[key]) {
                    complete = false
                }
            })
            if(complete) {
                return Promise.resolve(true)
            } else {
                return Promise.reject(false)
            }
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    onChange():Observable<any> {
        return this.subject.asObservable();
    }

    update():Promise<boolean> {
        this.subject.next();
        return Promise.resolve(true);
    }

    setHeartstepsId(heartstepsId:string):Promise<boolean> {
        return this.storage.set(storageKey, heartstepsId)
        .then(() => {
            return this.update();
        });
    }

    getHeartstepsId():Promise<string> {
        return this.storage.get(storageKey)
        .then((heartstepsId) => {
            if(heartstepsId) {
                return heartstepsId;
            } else {
                return Promise.reject(false)
            }
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    isEnrolled():Promise<boolean> {
        return this.getHeartstepsId()
        .then(() => {
            return Promise.resolve(true)
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    getProfile():Promise<any> {
        return Promise.all([
            this.checkNotificationsEnabled(),
            this.checkActivitySuggestions(),
            this.checkLocationPermission(),
            this.checkPlacesSet(),
            this.checkContactInformation(),
            this.checkReflectionTime()
        ])
        .then((results) => {
            return {
                notificationsEnabled: results[0],
                activitySuggestionTimes: results[1],
                locationPermission: results[2],
                places: results[3],
                participantInformation: results[4],
                weeklyReflectionTime: results[5]
            }
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    checkReflectionTime():Promise<boolean> {
        return this.reflectionTimeService.getTime()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    checkContactInformation():Promise<boolean> {
        return this.contactInformationService.get()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    checkNotificationsEnabled():Promise<boolean> {
        return this.notificationService.isEnabled()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    checkActivitySuggestions():Promise<boolean> {
        return this.activitySuggestionTimeService.getTimes()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    checkLocationPermission():Promise<boolean> {
        return this.geolocationService.hasPermission()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    checkPlacesSet():Promise<boolean> {
        return this.placesService.getLocations()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }
}