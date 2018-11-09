import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Storage } from "@ionic/storage";

@Injectable()
export class ActivitySuggestionTimeService{

    constructor(
        private heartstepsServer:HeartstepsServer,
        private storage:Storage
    ){}

    getTimeFields():Promise<any> {
        return Promise.resolve([
            { key:'morning', name:'Morning'},
            { key:'lunch', name:'Lunch'},
            { key:'midafternoon', name:'Afternoon'},
            { key:'evening', name:'Evening'},
            { key:'postdinner', name:'Post Dinner'}
        ])
    }

    getDefaultTimes():Promise<any> {
        return Promise.resolve({
            morning: "08:00",
            lunch: "12:00",
            midafternoon: "14:00",
            evening: "17:00",
            postdinner: "20:00"
        })
    }

    getTimes():Promise<any> {
        return this.storage.get('activity-suggestion-times')
        .then((times) => {
            if(times) {
                return times;
            } else {
                return Promise.reject("Unset times");
            }
            
        })
    }

    updateTimes(times:any):Promise<boolean> {
        return this.validateTimes(times)
        .then(() => {
            return this.saveTimes(times)
        })
        .then(() => {
            return Promise.resolve(true)
        })
    }

    validateTimes(times:any):Promise<boolean> {
        let errors = {
            required: [],
            outOfOrder: [],
            tooClose: []
        }

        let timesAsMinutes = {}
        Object.keys(times).forEach((key) => {
            let time = parseInt(times[key].split(':')[0]) * 60
            time += parseInt(times[key].split(':')[1])
            timesAsMinutes[key] = time
        })

        return this.getTimeFields()
        .then((timeFields) => {
            let previousField
            timeFields.forEach((timeField) => {
                if(previousField) {
                    let time = timesAsMinutes[timeField.key],
                        previousTime = timesAsMinutes[previousField.key]
                    if(previousTime > time) {
                        errors.outOfOrder.push(timeField.key)
                        errors.outOfOrder.push(previousField.key)
                    } else if(time - previousTime < 90) {
                        errors.tooClose.push(timeField.key)
                        errors.tooClose.push(previousField.key)
                    }
                }
                previousField = timeField
            })
            
            let hasErrors = false
            Object.keys(errors).forEach((key) => {
                if(errors[key].length) {
                    hasErrors = true
                }
            })

            if(hasErrors) {
                return Promise.reject(errors)
            } else {
                return Promise.resolve(true)
            }
        })
    }

    saveTimes(times:any):Promise<boolean> {
        return this.heartstepsServer.post(
            'activity-suggestions/times',
            times
        )
        .then((data) => {
            return this.storage.set('activity-suggestion-times', data)
        })
        .then(() => {
            return Promise.resolve(true)
        })
    }

}