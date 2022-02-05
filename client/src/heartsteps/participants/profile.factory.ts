import { Injectable } from "@angular/core";
import { MessageService } from "@heartsteps/notifications/message.service";
import { WalkingSuggestionTimeService } from "@heartsteps/walking-suggestions/walking-suggestion-time.service";
import { PlacesService } from "@heartsteps/places/places.service";
import { ContactInformationService } from "@heartsteps/contact-information/contact-information.service";
import { ReflectionTimeService } from "@heartsteps/weekly-survey/reflection-time.service";
import { FirstBoutPlanningTimeService } from "@heartsteps/bout-planning/first-bout-planning-time.service"
import { FitbitService } from "@heartsteps/fitbit/fitbit.service";
import { CurrentWeekService } from "@heartsteps/current-week/current-week.service";
import { DailyTimeService } from "@heartsteps/daily-times/daily-times.service";
import { ActivityPlanService } from "@heartsteps/activity-plans/activity-plan.service";
import { ActivityTypeService } from "@heartsteps/activity-types/activity-type.service";
import { CachedActivityLogService } from "@heartsteps/activity-logs/cached-activity-log.service";
import { ParticipantInformationService } from "./participant-information.service";
import { FitbitClockFaceService } from "@heartsteps/fitbit-clock-face/fitbit-clock-face.service";
import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";


@Injectable()
export class ProfileService {

    constructor(
        private messageService: MessageService,
        private dailyTimeService: DailyTimeService,
        private walkingSuggestionTimeService: WalkingSuggestionTimeService,
        private placesService: PlacesService,
        private contactInformationService: ContactInformationService,
        private reflectionTimeService: ReflectionTimeService,
        private firstBoutPlanningTimeService: FirstBoutPlanningTimeService,
        private fitbitService: FitbitService,
        private fitbitClockFaceService: FitbitClockFaceService,
        private featureFlagService: FeatureFlagService,
        private currentWeekService: CurrentWeekService,
        private cachedActivityLogService: CachedActivityLogService,
        private activityPlanService: ActivityPlanService,
        private activityTypeService: ActivityTypeService,
        private participantInformationService: ParticipantInformationService
    ) {
        console.log("src", "heartsteps", "participants", "profile.service.ts", "ProfileService", "constructor()");
    }

    public isComplete(): Promise<boolean> {
        console.log("ProfileService.isComplete() point 1", "revision", 1);
        return this.get()
            .then((profile) => {
                console.log("ProfileService.isComplete() point 2: profile=", profile);
                let complete = true
                console.log("ProfileService.isComplete() point 3");
                Object.keys(profile).forEach((key) => {
                    console.log("ProfileService.isComplete() point 4: key=", key);
                    if (!profile[key]) {
                        console.log("ProfileService.isComplete() point 5: profile['", key, "']=False");
                        complete = false
                    } else {
                        console.log("ProfileService.isComplete() point 5.2: profile['", key, "']=True");
                    }
                })
                if (complete) {
                    console.log("ProfileService.isComplete() point 6");
                    return Promise.resolve(true)
                } else {
                    console.log("ProfileService.isComplete() point 7");
                    return Promise.reject(false)
                }
            })
            .catch(() => {
                console.log("ProfileService.isComplete() point 8");
                return Promise.reject(false)
            })
    }

    public update(): Promise<void> {
        console.log('src', 'heartsteps', 'participants', 'profile.service.ts', 'ProfileService', 'update()');
        return Promise.all([
            this.fitbitService.setup(),
            this.loadCurrentWeek(),
            this.setupActivityLogCache(),
            this.setupActivityPlanService(),
            this.setupActivityTypeService(),
            this.setupDailyTimes(),
        ])
            .then(() => {
                console.log('src', 'heartsteps', 'participants', 'profile.service.ts', 'ProfileService', 'update()', 'return Promise.resolve()');
                return undefined;
            })
            .catch(() => {
                console.log('src', 'heartsteps', 'participants', 'profile.service.ts', 'update()', 'Error updating participant');
                return Promise.reject("Profile factory did not update participant");
            });
    }

    public load(): Promise<boolean> {
        console.log("ProfileService.load() point 1");
        var promiseArray = [];

        promiseArray.push(this.loadActivityLogCache());
        if (this.featureFlagService.hasFlagNP('walking_suggestions')) {
            promiseArray.push(this.loadWalkingSuggestionTimes());
        }
        if (this.featureFlagService.hasFlagNP('places')) {
            promiseArray.push(this.loadPlaces());
        }
        if (this.featureFlagService.hasFlagNP('weekly_reflection')) {
            promiseArray.push(this.loadReflectionTime());
        }
        if (this.featureFlagService.hasFlag('bout_planning')) {
            promiseArray.push(this.loadFirstBoutPlanningTime());
        }
        promiseArray.push(this.loadContactInformation());
        promiseArray.push(this.loadFitbit());
        if (this.featureFlagService.hasFlag('fitbit_clock_face')) {
            promiseArray.push(this.loadFitbitWatchStatus());
        }
        promiseArray.push(this.loadParticipantInformation());
        
        return Promise.all(promiseArray)
            .then(() => {
                return this.update();
            })
            .then(() => {
                return Promise.resolve(true);
            })
            .catch(() => {
                return Promise.resolve(false);
            });
    }

    public remove(): Promise<boolean> {
        return Promise.all([
            this.walkingSuggestionTimeService.removeTimes(),
            this.placesService.remove(),
            this.reflectionTimeService.remove(),
            this.firstBoutPlanningTimeService.remove(),
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

    public get(): Promise<any> {
        var profile = {}

        var promises = []

        promises.push(this.checkNotificationsEnabled());
        if (this.featureFlagService.hasFlagNP('walking_suggestions')) {
            promises.push(this.checkWalkingSuggestions());
        }
        if (this.featureFlagService.hasFlagNP('places')) {
            promises.push(this.checkPlacesSet());
        }
        if (this.featureFlagService.hasFlagNP('weekly_reflection')) {
            promises.push(this.checkReflectionTime());
        }
        if (this.featureFlagService.hasFlagNP('bout_planning')) {
            promises.push(this.checkFirstBoutPlanningTime());
        }
        promises.push(this.checkContactInformation());
        promises.push(this.checkFitbit());
        if (this.featureFlagService.hasFlagNP('fitbit_clock_face')) {
            promises.push(this.checkFitbitWatch());
        }

        return Promise.all(promises)
            .then((results) => {
                var index = 0;
                profile['notificationsEnabled'] = results[index]; index += 1;
                if (this.featureFlagService.hasFlagNP('walking_suggestions')) {
                    profile['walkingSuggestions'] = results[index]; index += 1;
                }
                if (this.featureFlagService.hasFlagNP('places')) {
                    profile['places'] = results[index]; index += 1;
                }
                if (this.featureFlagService.hasFlagNP('weekly_reflection')) {
                    profile['weeklyReflectionTime'] = results[index]; index += 1;
                }
                if (this.featureFlagService.hasFlagNP('bout_planning')) {
                    profile['firstBoutPlanningTime'] = results[index]; index += 1;
                }
                profile['contactInformation'] = results[index]; index += 1;
                profile['fitbitAuthorization'] = results[index]; index += 1;
                if (this.featureFlagService.hasFlagNP('fitbit_clock_face')) {
                    profile['fitbitClockFace'] = results[index]; index += 1;
                }

                return Promise.resolve(profile);
            })
            .catch(() => {
                console.log('src', 'heartsteps', 'participants', 'profile.service.ts', 'get()', 'point 3');
                return Promise.reject(undefined);
            });

    }

    private setupDailyTimes(): Promise<boolean> {
        return this.dailyTimeService.setup()
            .catch(() => {
                return Promise.resolve(false);
            });
    }

    private checkReflectionTime(): Promise<boolean> {
        return this.reflectionTimeService.getTime()
            .then(() => {
                return true
            })
            .catch(() => {
                return Promise.resolve(false)
            })
    }

    private checkFirstBoutPlanningTime(): Promise<boolean> {
        return this.featureFlagService.hasFlag('bout_planning')
            .then((hasFlag) => {
                if (hasFlag) {
                    return this.firstBoutPlanningTimeService.getTime()
                        .then(() => { return Promise.resolve(true) })
                        .catch(() => { return Promise.resolve(false) });
                } else {
                    return Promise.resolve(undefined);
                }
            });
    }

    private loadReflectionTime(): Promise<boolean> {
        return this.reflectionTimeService.load()
            .then(() => {
                return true;
            })
            .catch(() => {
                return Promise.resolve(false);
            });
    }

    private loadFirstBoutPlanningTime(): Promise<boolean> {
        return this.featureFlagService.hasFlag("bout_planning")
            .then((hasFlag) => {
                if (hasFlag) {
                    return this.firstBoutPlanningTimeService.load()
                        .then(() => { return Promise.resolve(true); });
                } else {
                    return Promise.resolve(false);
                }
            });
    }

    private checkContactInformation(): Promise<boolean> {
        return this.contactInformationService.get()
            .then(() => {
                return true
            })
            .catch(() => {
                return Promise.resolve(false)
            })
    }

    private loadContactInformation(): Promise<boolean> {
        return this.contactInformationService.load()
            .then(() => {
                return true;
            })
            .catch(() => {
                return Promise.resolve(false);
            });
    }

    private checkNotificationsEnabled(): Promise<boolean> {
        return this.messageService.requestedPermission()
            .then(() => {
                return true
            })
            .catch(() => {
                return Promise.resolve(false)
            })
    }

    private checkWalkingSuggestions(): Promise<boolean> {
        return this.walkingSuggestionTimeService.getTimes()
            .then(() => {
                return true
            })
            .catch(() => {
                return Promise.resolve(false)
            })
    }

    private loadWalkingSuggestionTimes(): Promise<boolean> {
        return this.walkingSuggestionTimeService.getTimes()
            .catch(() => {
                return this.walkingSuggestionTimeService.loadTimes()
            })
            .then(() => {
                return true;
            })
            .catch(() => {
                return false
            });
    }

    private checkPlacesSet(): Promise<boolean> {
        return this.placesService.getLocations()
            .then(() => {
                return true
            })
            .catch(() => {
                return Promise.resolve(false)
            })
    }

    private loadPlaces(): Promise<boolean> {
        return this.placesService.load()
            .then(() => {
                return true;
            })
            .catch(() => {
                return Promise.resolve(false);
            })
    }

    private checkFitbit(): Promise<boolean> {
        return this.fitbitService.isAuthorized()
            .then(() => {
                return true;
            })
            .catch(() => {
                return Promise.resolve(false);
            });
    }

    private loadFitbit(): Promise<boolean> {
        return this.fitbitService.updateAuthorization()
            .then(() => {
                return true;
            })
            .catch(() => {
                return Promise.resolve(false);
            });
    }

    private loadCurrentWeek(): Promise<boolean> {
        return this.currentWeekService.setup()
            .then(() => {
                return true;
            })
            .catch(() => {
                return Promise.resolve(false);
            })
    }

    private setupActivityLogCache(): Promise<boolean> {
        return this.cachedActivityLogService.reload()
            .then(() => {
                return true;
            })
            .catch(() => {
                return Promise.resolve(false);
            })
    }

    private loadActivityLogCache(): Promise<boolean> {
        return this.cachedActivityLogService.update()
            .then(() => {
                return true;
            })
            .catch(() => {
                return false;
            })
    }

    private setupActivityPlanService() {
        return this.activityPlanService.setup()
            .then(() => {
                return true;
            })
            .catch(() => {
                return Promise.resolve(false);
            })
    }

    private setupActivityTypeService(): Promise<boolean> {
        return this.activityTypeService.setup()
            .then(() => {
                return true;
            })
            .catch(() => {
                return Promise.resolve(false);
            })
    }

    private loadParticipantInformation() {
        return this.participantInformationService.load()
            .then(() => {
                return true
            })
            .catch(() => {
                return Promise.resolve(false);
            })
    }

    private checkFitbitWatch(): Promise<boolean> {
        return this.featureFlagService.hasFlag("fitbit_clockface")
            .then((hasFlag) => {
                if (hasFlag) {
                    return this.fitbitClockFaceService.isPaired()
                        .then((isPaired) => { return Promise.resolve(isPaired); });
                } else {
                    return Promise.resolve(undefined);
                }
            });
    }

    private loadFitbitWatchStatus(): Promise<boolean> {
        return this.featureFlagService.hasFlag("fitbit_clockface")
            .then((hasFlag) => {
                if (hasFlag) {
                    return this.fitbitClockFaceService.update()
                        .then(() => { return Promise.resolve(true); });
                } else {
                    return Promise.resolve(false);
                }
            });
    }
}