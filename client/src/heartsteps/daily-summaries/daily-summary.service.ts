import * as moment from 'moment';

import { Injectable, EventEmitter } from "@angular/core";
import { DailySummary } from "./daily-summary.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { DailySummarySerializer } from './daily-summary.serializer';

const dateFormat = 'YYYY-MM-DD';

@Injectable()
export class DailySummaryService {

    public updated: EventEmitter<DailySummary> = new EventEmitter();

    constructor(
        private heartstepsServer: HeartstepsServer,
        private serializer: DailySummarySerializer
    ) {}

    public get(date: Date): Promise<DailySummary> {
        const dateFormatted:string = moment(date).format(dateFormat);
        return this.heartstepsServer.get(`/activity/summary/${dateFormatted}`)
        .then((response:any) => {
            const summary = this.deserializeSummary(response);
            return summary;
        });
    }

    public update(date: Date): Promise<DailySummary> {
        const dateFormatted:string = moment(date).format(dateFormat);
        return this.heartstepsServer.get(`/activity/summary/update/${dateFormatted}`)
        .then((response:any) => {
            const summary = this.deserializeSummary(response);
            this.updated.emit(summary);
            return summary;
        });
    }

    public getWeek(start: Date, end:Date):Promise<Array<DailySummary>> {
        const startFormatted = moment(start).format(dateFormat);
        const endFormatted = moment(end).format(dateFormat);
        return this.heartstepsServer.get(`activity/summary/${startFormatted}/${endFormatted}`)
        .then((response:Array<any>) => {
            const summaries:Array<DailySummary> = [];
            response.forEach((res)=> {
                summaries.push(this.deserializeSummary(res));
            })
            return summaries;
        });
    }

    private deserializeSummary(data:any):DailySummary {
        return this.serializer.deserialize(data);
    }
}
