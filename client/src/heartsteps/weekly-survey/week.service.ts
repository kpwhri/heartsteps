import { Injectable } from "@angular/core";
import { Week } from "./week.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import * as moment from 'moment';

@Injectable()
export class WeekService {
    
    constructor(
        private heartstepsServer: HeartstepsServer
    ){}

    getWeek(weekId:string):Promise<Week> {
        return this.heartstepsServer.get('weeks/'+weekId)
        .then((data:any) => {
            return this.deserializeWeek(data);
        })
        .then((week:Week) => {
            return this.getWeekGoal(week);
        });
    }

    getWeekGoal(week:Week):Promise<Week> {
        return this.heartstepsServer.get('weeks/' + week.id + '/goal')
        .then((data) => {
            week.goal = data.minutes;
            week.confidence = data.confidence;
            return week;
        });
    }

    setWeekGoal(week:Week, minutes:number, confidence:number):Promise<Week> {
        return this.heartstepsServer.post('weeks/' + week.id + '/goal', {
            minutes: minutes,
            confidence: confidence
        })
        .then(() => {
            week.goal = minutes;
            week.confidence = confidence;
            return week;
        });
    }

    public getCurrentWeek():Promise<Week> {
        return this.heartstepsServer.get('weeks/current')
        .then((data:any) => {
            return this.deserializeWeek(data);
        })
        .then((week:Week) => {
            return this.getWeekGoal(week);
        });
    }

    getWeekAfter(week:Week):Promise<Week> {
        return this.heartstepsServer.get('weeks/' + week.id + '/next')
        .then((data:any) => {
            return this.deserializeWeek(data);
        })
        .then((week:Week) => {
            return this.getWeekGoal(week);
        });
    }

    public deserializeWeek(data:any):Week {
        const week = new Week(this);
        week.id = data.id;
        week.start = moment(data.start, 'YYYY-MM-DD').toDate();
        week.end = moment(data.end, 'YYYY-MM-DD').endOf('day').toDate();
        if(data.goal) week.goal = data.goal;
        if(data.confidence) week.confidence = data.confidence;
        return week;
    }

    public serializeWeek(week:Week):any {
        const serialized:any = {
            id: week.id,
            start: moment(week.start).format('YYYY-MM-DD'),
            end: moment(week.end).format('YYYY-MM-DD'),
        };
        if(week.goal !== undefined) {
            serialized['goal'] = week.goal;
        }
        if(week.confidence !== undefined) {
            serialized['confidence'] = week.confidence;
        }
        return serialized;
    }

}