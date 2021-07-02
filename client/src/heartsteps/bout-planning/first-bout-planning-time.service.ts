import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { DateFactory } from "@infrastructure/date.factory";

// const storageKey = 'weeklyReflectionTime'
const storageKey = 'firstBoutPlanningTime'

// export class ReflectionTime {
//     public day: string;
//     public time: Date;
// }

export class FirstBoutPlanningTime {
    public time: Date;
}



@Injectable()
// export class ReflectionTimeService{
export class FirstBoutPlanningTimeService {

    constructor(
        private heartstepsServer: HeartstepsServer,
        private storage: Storage,
        private dateFactory: DateFactory
    ) { }

    // public getTime(): Promise<ReflectionTime> {
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

    // public getDefaultReflectionTime(): Promise<ReflectionTime> {
    public getDefaultFirstBoutPlanningTime(): Promise<FirstBoutPlanningTime> {
        return Promise.resolve({
            time: this.dateFactory.parseTime('07:00')
        });
    }

    // public setTime(reflectionTime: ReflectionTime): Promise<boolean> {
    public setTime(firstBoutPlanningTime: FirstBoutPlanningTime): Promise<boolean> {
        // const data: any = this.serialize(reflectionTime);
        const data: any = this.serialize(firstBoutPlanningTime);
        // return this.heartstepsServer.post('reflection-time', data)
        return this.heartstepsServer.post('first-bout-planning-time', data)
            .then(() => {
                return this.set(data);
            })
            .then(() => {
                return true;
            })
    }

    public load(): Promise<boolean> {
        // return this.heartstepsServer.get('reflection-time')
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

    // private serialize(reflectionTime: ReflectionTime) {
    private serialize(firstBoutPlanningTime: FirstBoutPlanningTime) {
        return {
            // day: reflectionTime.day,
            // time: this.dateFactory.formatTime(reflectionTime.time)
            time: this.dateFactory.formatTime(firstBoutPlanningTime.time)
        }
    }

    // private deserialize(data: any): ReflectionTime {
    //     const reflectionTime = new ReflectionTime();
    private deserialize(data: any): FirstBoutPlanningTime {
        const firstBoutPlanningTime = new FirstBoutPlanningTime();
        // reflectionTime.day = data.day;
        // reflectionTime.time = this.dateFactory.parseTime(data.time);
        firstBoutPlanningTime.time = this.dateFactory.parseTime(data.time);
        // return reflectionTime;
        return firstBoutPlanningTime;
    }

}