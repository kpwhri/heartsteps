import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { StorageService } from "@infrastructure/storage.service";
import { format } from "util";

const storageKey:string = 'activity-suggestion-times'

@Injectable()
export class WalkingSuggestionTimeService{

    constructor(
        private heartstepsServer:HeartstepsServer,
        private storage:StorageService
    ){}

    getTimeFields():Promise<Array<any>> {
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
            morning: this.parseTime("08:00"),
            lunch: this.parseTime("12:00"),
            midafternoon: this.parseTime("14:00"),
            evening: this.parseTime("17:00"),
            postdinner: this.parseTime("20:00")
        });
    }

    getTimes():Promise<any> {
        return this.storage.get(storageKey)
        .then((times) => {
            const timesAsDates = {}
            Object.keys(times).forEach((key) => {
                timesAsDates[key] = this.parseTime(times[key]);
            })
            return timesAsDates;
        })
        .catch(() => {
            return Promise.reject("No saved suggestion times");
        })
    }

    setTimes(times):Promise<any> {
        return this.storage.set(storageKey, times)
        .then(() => {
            return times;
        });
    }

    removeTimes():Promise<any> {
        return this.storage.remove(storageKey);
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

        return this.getTimeFields()
        .then((timeFields) => {
            let previousField
            timeFields.forEach((timeField) => {
                if(previousField) {
                    let time = times[timeField.key],
                        previousTime = times[previousField.key]
                    const differenceInMinutes = (time.getTime() - previousTime.getTime())/(1000 * 60);
                    if(previousTime > time) {
                        errors.outOfOrder.push(timeField.key)
                        errors.outOfOrder.push(previousField.key)
                    } else if(differenceInMinutes < 90) {
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
        const formattedTimes = {};
        Object.keys(times).forEach((key) => {
            formattedTimes[key] = this.formatTime(times[key]);
        });
        return this.heartstepsServer.post(
            'walking-suggestions/times/',
            formattedTimes
        )
        .then((data) => {
            return this.setTimes(data);
        })
        .then(() => {
            return Promise.resolve(true)
        })
    }

    loadTimes():Promise<any> {
        return this.getTimes()
        .catch(() => {
            return this.heartstepsServer.get('walking-suggestions/times/');
        })
        .then((times) => {
            return this.setTimes(times);
        });
    }

    private parseTime(time: string): Date {
        const parts = time.split(':');

        let date = new Date();
        date.setHours(Number(parts[0]));
        date.setMinutes(Number(parts[1]));
        return date;
    }

    private formatTime(date: Date): string {
        return date.getHours() + ':' + date.getMinutes();
    }

}