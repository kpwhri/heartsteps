import { Injectable } from "@angular/core";
import { Week } from "./week.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";


@Injectable()
export class WeekService {
    
    constructor(
        private heartstepsServer: HeartstepsServer
    ){}

    getCurrentWeek():Promise<Week> {
        return this.heartstepsServer.get('weeks')
        .then((data:any) => {
            const week = new Week();
            week.id = data.id;
            week.start = new Date(data.start);
            week.end = new Date(data.end);
            return week;
        });
    }

}