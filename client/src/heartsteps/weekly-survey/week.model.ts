import { WeekService } from "./week.service";

export class Week {
    id:string;
    start:Date;
    end:Date;
    goal:number;
    confidence: number;

    constructor(
        private weekService:WeekService
    ){}

    setGoal(minutes:number, confidence:number):Promise<boolean> {
        return this.weekService.setWeekGoal(this, minutes, confidence)
        .then(() => {
            return true;
        });
    }
}
