import { Injectable } from "@angular/core";
import { Week } from "./week.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import * as moment from 'moment';
import { WeekSerializer } from "./week.serializer";

@Injectable()
export class WeekService {
    
    constructor(
        private heartstepsServer: HeartstepsServer,
        private weekSerializer: WeekSerializer
    ){}

    getWeek(weekId:string):Promise<Week> {
        return this.heartstepsServer.get('weeks/'+weekId)
        .then((data:any) => {
            return this.deserializeWeek(data);
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
        return this.heartstepsServer.post('weeks/' + week.id, {
            goal: minutes,
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

    public deserializeWeek(data:any):Week {
        return this.weekSerializer.deserialize(data);
    }

    public serializeWeek(week:Week):any {
        return this.weekSerializer.serialize(week);
    }

}