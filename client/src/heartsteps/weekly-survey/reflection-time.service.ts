import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { DateFactory } from "@infrastructure/date.factory";

const storageKey = 'weeklyReflectionTime'

export class ReflectionTime {
    public day: string;
    public time: Date;
}

@Injectable()
export class ReflectionTimeService{

    constructor(
        private heartstepsServer:HeartstepsServer,
        private storage:Storage,
        private dateFactory: DateFactory
    ){}

    getTime():Promise<ReflectionTime> {
        return this.storage.get(storageKey)
        .then((data) => {
            if(data) {
                return Promise.resolve(this.deserialize(data));
            } else {
                return Promise.reject(false);
            }
        })
        .catch(() => {
            return Promise.reject(false);
        })
    }

    public getDefaultReflectionTime():Promise<ReflectionTime> {
        return Promise.resolve({
            day: 'sunday',
            time: this.dateFactory.parseTime('20:00')
        });
    }

    setTime(reflectionTime:ReflectionTime):Promise<boolean> {
        const data:any = this.serialize(reflectionTime);
        return this.heartstepsServer.post('reflection-time', data)
        .then(() => {
            return this.set(data);
        })
        .then(() => {
            return true;
        })
    }

    load():Promise<boolean> {
        return this.heartstepsServer.get('reflection-time')
        .then((time) => {
            return this.set(time);
        })
        .then(() => {
            return Promise.resolve(true);
        });
    }

    set(time:any):Promise<any> {
        return this.storage.set(storageKey, time)
        .then(() => {
            return time;
        });
    }

    remove():Promise<boolean> {
        // TODO: Remove reflection time from server
        return this.storage.remove(storageKey);
    }

    private serialize(reflectionTime: ReflectionTime) {
        return {
            day: reflectionTime.day,
            time: this.dateFactory.formatTime(reflectionTime.time)
        }
    }

    private deserialize(data:any):ReflectionTime {
        const reflectionTime = new ReflectionTime();
        reflectionTime.day = data.day;
        reflectionTime.time = this.dateFactory.parseTime(data.time);
        return reflectionTime;
    }

}