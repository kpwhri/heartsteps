import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { DateFactory } from "@infrastructure/date.factory";

const storageKey = 'firstBoutPlanningTime'

export class FirstBoutPlanningTime {
    public time: Date;
}



@Injectable()
export class FirstBoutPlanningTimeService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private storage: Storage,
        private dateFactory: DateFactory
    ) { }

    public getTime(): Promise<FirstBoutPlanningTime> {
        return this.storage.get(storageKey)
            .then((data) => {
                if (data) {
                    return Promise.resolve(this.deserialize(data));
                } else {
                    return Promise.reject(false);
                }
            })
            .catch(() => {
                return Promise.reject(false);
            })
    }

    public getDefaultFirstBoutPlanningTime(): Promise<FirstBoutPlanningTime> {
        return Promise.resolve({
            time: this.dateFactory.parseTime('07:00')
        });
    }

    public setTime(firstBoutPlanningTime: FirstBoutPlanningTime): Promise<boolean> {
        const data: any = this.serialize(firstBoutPlanningTime);
        return this.heartstepsServer.post('first-bout-planning-time', data)
            .then(() => {
                return this.set(data);
            })
            .then(() => {
                return true;
            })
    }

    public load(): Promise<boolean> {
        return this.heartstepsServer.get('first-bout-planning-time')
            .then((time) => {
                return this.set(time);
            })
            .then(() => {
                return Promise.resolve(true);
            });
    }

    private set(time: any): Promise<any> {
        return this.storage.set(storageKey, time)
            .then(() => {
                return time;
            });
    }

    public remove(): Promise<boolean> {
        return this.storage.remove(storageKey);
    }

    private serialize(firstBoutPlanningTime: FirstBoutPlanningTime) {
        return {
            time: this.dateFactory.formatTime(firstBoutPlanningTime.time)
        }
    }

    private deserialize(data: any): FirstBoutPlanningTime {
        const firstBoutPlanningTime = new FirstBoutPlanningTime();
        firstBoutPlanningTime.time = this.dateFactory.parseTime(data.time);
        return firstBoutPlanningTime;
    }

}