import { Injectable } from "@angular/core";
import { Week } from "./week.model";


@Injectable()
export class WeekService {
    
    constructor(){}

    getCurrentWeek():Promise<Week> {
        const week = new Week();
        week.id = "1234";
        return Promise.resolve(week);
    }

}