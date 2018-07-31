import { Injectable } from "@angular/core";
import { HeartstepsServer } from "../infrastructure/heartsteps-server.service";
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

    getTimes():Promise<any> {
        return this.storage.get('activity-suggestion-times')
        .then((times) => {
            if(!times) {
                return {}
            } else {
                return times
            }
        })
        .catch(() => {
            return {}
        })
    }

    updateTimes(times:any):Promise<boolean> {
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