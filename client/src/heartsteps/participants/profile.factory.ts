import { Injectable } from "@angular/core";
import { MessageService } from "@heartsteps/notifications/message.service";
import { WalkingSuggestionTimeService } from "@heartsteps/walking-suggestions/walking-suggestion-time.service";
import { LocationService } from "@infrastructure/location.service";
import { PlacesService } from "@heartsteps/places/places.service";
import { ContactInformationService } from "@heartsteps/contact-information/contact-information.service";
import { ReflectionTimeService } from "@heartsteps/weekly-survey/reflection-time.service";
import { FitbitService } from "@heartsteps/fitbit/fitbit.service";


@Injectable()
export class ProfileService {

    constructor(
        private messageService: MessageService,
        private walkingSuggestionTimeService:WalkingSuggestionTimeService,
        private locationService:LocationService,
        private placesService:PlacesService,
        private contactInformationService: ContactInformationService,
        private reflectionTimeService: ReflectionTimeService,
        private fitbitService: FitbitService
    ) {}

    public isComplete():Promise<boolean> {
        return this.get()
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

    public load():Promise<boolean> {
        return Promise.all([
            this.loadWalkingSuggestions(),
            this.loadPlaces(),
            this.loadReflectionTime(),
            this.loadContactInformation(),
            this.loadFitbit()
        ])
        .then(() => {
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.reject("Complete participant did not load");
        });
    }

    public remove():Promise<boolean> {
        return Promise.all([
            this.walkingSuggestionTimeService.removeTimes(),
            this.messageService.disable(),
            this.locationService.removePermission(),
            this.placesService.remove(),
            this.reflectionTimeService.remove(),
            this.contactInformationService.remove(),
            this.fitbitService.remove()
        ])
        .then(() => {
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.reject("Error removing participant");
        });
    }

    public get():Promise<any> {
        return Promise.all([
            this.checkNotificationsEnabled(),
            this.checkWalkingSuggestions(),
            this.checkLocationPermission(),
            this.checkPlacesSet(),
            this.checkReflectionTime(),
            this.checkContactInformation(),
            this.checkFitbit()
        ])
        .then((results) => {
            return {
                notificationsEnabled: results[0],
                walkingSuggestionTimes: results[1],
                locationPermission: results[2],
                places: results[3],
                weeklyReflectionTime: results[4],
                contactInformation: results[5],
                fitbitAuthorization: results[6]
            }
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    private checkReflectionTime():Promise<boolean> {
        return this.reflectionTimeService.getTime()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    private loadReflectionTime():Promise<boolean> {
        return this.reflectionTimeService.load()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    private checkContactInformation():Promise<boolean> {
        return this.contactInformationService.get()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    private loadContactInformation():Promise<boolean> {
        return this.contactInformationService.load()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    private checkNotificationsEnabled():Promise<boolean> {
        return this.messageService.isEnabled()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    private checkWalkingSuggestions():Promise<boolean> {
        return this.walkingSuggestionTimeService.getTimes()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    private loadWalkingSuggestions():Promise<boolean> {
        return this.walkingSuggestionTimeService.loadTimes()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        })
    }

    private checkLocationPermission():Promise<boolean> {
        return this.locationService.hasPermission()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    private checkPlacesSet():Promise<boolean> {
        return this.placesService.getLocations()
        .then(() => {
            return true
        })
        .catch(() => {
            return Promise.resolve(false)
        })
    }

    private loadPlaces():Promise<boolean> {
        return this.placesService.load()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        })
    }

    checkFitbit():Promise<boolean> {
        return this.fitbitService.isAuthorized()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }

    loadFitbit():Promise<boolean> {
        return this.fitbitService.updateAuthorization()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.resolve(false);
        });
    }
}