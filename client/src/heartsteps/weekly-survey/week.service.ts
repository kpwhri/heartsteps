import { Injectable } from "@angular/core";
import { Week } from "./week.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";

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

    setWeekGoal(week:Week):Promise<Week> {
        return this.heartstepsServer.post('weeks/' + week.id + '/goal', {
            minutes: week.goal,
            confidence: week.confidence
        })
        .then(() => {
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

    private deserializeWeek(data:any):Week {
        const week = new Week();
        week.id = data.id;
        week.start = new Date(data.start);
        week.end = new Date(data.end);
        return week;
    }

}