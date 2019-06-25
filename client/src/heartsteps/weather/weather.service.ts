import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { DocumentStorageService, DocumentStorage } from "@infrastructure/document-storage.service";
import { DailyWeather } from "./daily-weather.model";
import { Observable, Subject } from "rxjs";
import * as moment from 'moment';


@Injectable()
export class WeatherService {

    private storage: DocumentStorage

    constructor(
        private heartstepsServer: HeartstepsServer,
        storage: DocumentStorageService
    ) {
        this.storage = storage.create('weather');
    }

    public get(date: Date): Promise<DailyWeather> {
        const date_string = moment(date).format('YYYY-MM-DD')
        return this.heartstepsServer.get('weather/'+date_string)
        .then((forecast: any) => {
            return this.deserialize(forecast);
        });
    }

    public update(date: Date): Promise<DailyWeather> {
        return this.get(date);
    }

    public watch(date: Date): Observable<DailyWeather> {
        const subject: Subject<DailyWeather> = new Subject();

        this.get(date).then((weather) => {
            subject.next(weather);
        });

        return subject.asObservable();
    }

    private deserialize(data:any): DailyWeather {
        const weather = new DailyWeather();
        weather.category = data['category'];
        weather.date = data['date'];
        weather.high = data['high'];
        weather.low = data['low'];
        return weather;
    }

}
