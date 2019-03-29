import { Injectable, EventEmitter } from "@angular/core";
import { DailySummary } from "./daily-summary.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { DailySummarySerializer } from './daily-summary.serializer';

@Injectable()
export class DailySummaryService {

    public updated: EventEmitter<DailySummary> = new EventEmitter();

    constructor(
        private heartstepsServer: HeartstepsServer,
        private serializer: DailySummarySerializer
    ) {}

    public get(date: Date): Promise<DailySummary> {
        const dateFormatted:string = this.serializer.formatDate(date);
        return this.heartstepsServer.get(`/activity/summary/${dateFormatted}`)
        .then((response:any) => {
            return this.serializer.deserialize(response);
        });
    }

    public update(date: Date): Promise<DailySummary> {
        const dateFormatted:string = this.serializer.formatDate(date);
        return this.heartstepsServer.get(`/activity/summary/update/${dateFormatted}`)
        .then((response:any) => {
            const summary = this.serializer.deserialize(response);
            this.updated.emit(summary);
            return summary;
        });
    }

    public getWeek(start: Date, end:Date):Promise<Array<DailySummary>> {
        const startFormatted = this.serializer.formatDate(start);
        const endFormatted = this.serializer.formatDate(end);
        return this.heartstepsServer.get(`activity/summary/${startFormatted}/${endFormatted}`)
        .then((response:Array<any>) => {
            const summaries:Array<DailySummary> = [];
            response.forEach((item)=> {
                const summary = this.serializer.deserialize(item)
                summaries.push(summary);
            })
            return summaries;
        });
    }

}
