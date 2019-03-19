import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";

export class DailyTime {
    public key: string;
    public name: string;
    public value?: string;
    public default?: string;
}

@Injectable()
export class DailyTimeService {

    public times:BehaviorSubject<Array<DailyTime>> = new BehaviorSubject(undefined);

    constructor() {}

    public setup():Promise<boolean> {

        this.loadDefaultTimes();

        return Promise.resolve(true);
    }

    private loadDefaultTimes():Promise<boolean> {
        const times:Array<DailyTime> = [
            { key:'morning', name:'Morning'},
            { key:'lunch', name:'Lunch'},
            { key:'midafternoon', name:'Afternoon'},
            { key:'evening', name:'Evening'},
            { key:'postdinner', name:'Post Dinner'} 
        ]
        this.times.next(times);
        return Promise.resolve(true);
    }

}
