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
        return this.storage.get(date_string)
        .then((data) => {
            return this.deserialize(data)
        })
        .catch(() => {
            return this.update(date);
        });
    }

    public update(date: Date): Promise<DailyWeather> {
        const date_string = moment(date).format('YYYY-MM-DD')
        return this.heartstepsServer.get('weather/'+date_string)
        .then((data: any) => {
            const forecast = this.deserialize(data);
            return this.store(forecast);
        });
    }

    public watch(date: Date): Observable<DailyWeather> {
        const subject: Subject<DailyWeather> = new Subject();

        this.get(date).then((weather) => {
            subject.next(weather);
        });

        return subject.asObservable();
    }

    private store(forecast: DailyWeather): Promise<DailyWeather> {
        const serialized = this.serialize(forecast);
        return this.storage.set(serialized.date, serialized)
        .then(() => {
            return forecast
        });
    }

    private deserialize(data:any): DailyWeather {
        const weather = new DailyWeather();
        weather.category = data['category'];
        weather.date = moment(data['date'], 'YYYY-MM-DD').toDate();
        weather.high = data['high'];
        weather.low = data['low'];
        return weather;
    }

    private serialize(forecast: DailyWeather): any {
        return {
            'date': moment(forecast.date).format('YYYY-MM-DD'),
            'category': forecast.category,
            'high': forecast.high,
            'low': forecast.low
        }
    }

}
