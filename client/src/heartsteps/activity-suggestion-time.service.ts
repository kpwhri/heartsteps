import { Injectable } from "@angular/core";
import { HeartstepsServer } from "../infrastructure/heartsteps-server.service";
import { Storage } from "@ionic/storage";

declare var Intl:any

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

    getTimes():Promise<any> {
        return this.storage.get('activity-suggestion-times')
        .then((timesArray) => {
            let times = {}
            if(!timesArray) {
                return times
            }

            timesArray.forEach(time => {
                times[time.type] = time.hour + ":" + time.minute;
            })
            return times
        })
        .catch(() => {
            return {}
        })
    }

    updateTimes(times:any):Promise<boolean> {
        let timesArray = []
        Object.keys(times).forEach((timeType) => {
            const timeParts = times[timeType].split(":")
            timesArray.push({
                type: timeType,
                hour: timeParts[0],
                minute: timeParts[0],
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            })
        })

        return this.heartstepsServer.post(
            'activity-suggestions/times',
            {
                'times': timesArray
            }
        )
        .then((data) => {
            return this.storage.set('activity-suggestion-times', data)
        })
        .then(() => {
            return Promise.resolve(true)
        })
    }

}