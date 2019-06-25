import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { DocumentStorageService, DocumentStorage } from "@infrastructure/document-storage.service";
import { DailyWeather } from "./daily-weather.model";
import { Observable, Subject } from "rxjs";


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
        const weather = new DailyWeather();
        weather.category = 'cloudy';
        weather.high = 75;
        weather.low = 60;
        return Promise.resolve(weather);
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

}
