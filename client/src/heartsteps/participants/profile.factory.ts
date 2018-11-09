import { Injectable } from "@angular/core";
import { NotificationService } from "@heartsteps/notifications/notification.service";
import { ActivitySuggestionTimeService } from "@heartsteps/activity-suggestions/activity-suggestion-time.service";
import { LocationService as GeolocationService } from "@infrastructure/location.service";
import { PlacesService } from "@heartsteps/places/places.service";
import { ContactInformationService } from "@heartsteps/contact-information/contact-information.service";
import { ReflectionTimeService } from "@heartsteps/weekly-survey/reflection-time.service";
import { FitbitService } from "@heartsteps/fitbit/fitbit.service";


@Injectable()
export class ProfileService {

    constructor(
        private notificationService: NotificationService,
        private activitySuggestionTimeService:ActivitySuggestionTimeService,
        private geolocationService:GeolocationService,
        private placesService:PlacesService,
        private contactInformationService: ContactInformationService,
        private reflectionTimeService: ReflectionTimeService,
        private fitbitService: FitbitService
    ) {}

    isComplete():Promise<boolean> {
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

    getProfile():Promise<any> {
        return Promise.all([
            this.checkNotificationsEnabled(),
            this.checkActivitySuggestions(),
            this.checkLocationPermission(),
            this.checkPlacesSet(),
            this.checkReflectionTime(),
            this.checkFitbit()
        ])
        .then((results) => {
            return {
                notificationsEnabled: results[0],
                activitySuggestionTimes: results[1],
                locationPermission: results[2],
                places: results[3],
                weeklyReflectionTime: results[4],
                fitbit: results[5]
            }
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    checkFitbit():Promise<boolean> {
        return this.fitbitService.isAuthorized()
        .then(() => {
            return true;
        })
        .catch(() => {
            return false;
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