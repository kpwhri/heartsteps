import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { StorageService } from "@infrastructure/storage.service";

const storageKey:string = 'activity-suggestion-times'

@Injectable()
export class WalkingSuggestionTimeService{

    constructor(
        private heartstepsServer:HeartstepsServer,
        private storage:StorageService
    ){}

    public getTimeFields():Promise<Array<any>> {
        return Promise.resolve([
            { key:'morning', name:'Morning'},
            { key:'lunch', name:'Lunch'},
            { key:'midafternoon', name:'Afternoon'},
            { key:'evening', name:'Evening'},
            { key:'postdinner', name:'Post Dinner'}
        ])
    }

    public getDefaultTimes():Promise<any> {
        return Promise.resolve({
            morning: this.parseTime("08:00"),
            lunch: this.parseTime("12:00"),
            midafternoon: this.parseTime("14:00"),
            evening: this.parseTime("17:00"),
            postdinner: this.parseTime("20:00")
        });
    }

    public getTimes():Promise<any> {
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

    public setTimes(times):Promise<any> {
        return this.storage.set(storageKey, times)
        .then(() => {
            return times;
        });
    }

    public removeTimes():Promise<any> {
        return this.storage.remove(storageKey);
    }

    public updateTimes(times:any):Promise<boolean> {
        return this.validateTimes(times)
        .then(() => {
            return this.saveTimes(times)
        })
        .then(() => {
            return Promise.resolve(true)
        })
    }

    public validateTimes(times:any):Promise<boolean> {
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

    public saveTimes(times:any):Promise<boolean> {
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

    public loadTimes():Promise<any> {
        return this.getTimes()
        .catch(() => {
            return this.heartstepsServer.get('walking-suggestions/times/')
            .then((times) => {
                return this.setTimes(times);
            });
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