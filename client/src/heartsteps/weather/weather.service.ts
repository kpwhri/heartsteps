import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { DocumentStorageService, DocumentStorage } from "@infrastructure/document-storage.service";
import { DailyWeather } from "./daily-weather.model";
import { Observable, Subject } from "rxjs";
import * as moment from 'moment';
import { DateFactory } from "@infrastructure/date.factory";


@Injectable()
export class WeatherService {

    private storage: DocumentStorage

    constructor(
        private heartstepsServer: HeartstepsServer,
        private dateFactory: DateFactory,
        storage: DocumentStorageService
    ) {
        this.storage = storage.create('weather');
    }

    public get(date: Date): Promise<DailyWeather> {
        return this.retrieve(date)
        .then((data) => {
            return this.deserialize(data)
        })
        .catch(() => {
            return this.update(date);
        });
    }

    public watch(date: Date): Observable<DailyWeather> {
        const subject: Subject<DailyWeather> = new Subject();
        this.retrieve(date)
        .then((forecast) => {
            subject.next(forecast);
            this.update(date);
        })
        .catch(() => {
            this.load(date)
            .then((forecast) => {
                subject.next(forecast);
                console.log('Try to store date', date);
                if(this.canStoreDate(date)) {
                    console.log('Storing date', date);
                    this.store(forecast);
                }
            })
            .catch(() => {
                console.log('Weather service failed to update weather');
            });
        });

        return subject.asObservable();
    }

    public updateCache(): Promise<void> {
        return this.retrieveAll()
        .then((forecasts) => {
            const forecasts_to_save = forecasts.filter((forecast) => {
                return this.canStoreDate(forecast.date);
            });
            return this.storeAll(forecasts_to_save);
        })
        .then(() => {
            return undefined;
        });
    }

    private update(date: Date): Promise<DailyWeather> {
        return this.load(date)
        .then((forecast) => {
            return this.store(forecast);
        });
    }

    private load(date: Date): Promise<DailyWeather> {
        const date_string = moment(date).format('YYYY-MM-DD')
        return this.heartstepsServer.get('weather/'+date_string)
        .then((data: any) => {
            return this.deserialize(data);
        });
    }

    private retrieve(date: Date): Promise<DailyWeather> {
        const date_string = moment(date).format('YYYY-MM-DD')
        return this.storage.get(date_string);
    }

    private retrieveAll(): Promise<Array<DailyWeather>> {
        return this.storage.getList()
        .then((storedObjects) => {
            return storedObjects.map((data) => {
                return this.deserialize(data)
            })
        });
    }

    private storeAll(forecasts: Array<DailyWeather>): Promise<Array<DailyWeather>> {
        const forecastsObj = {};
        forecasts.forEach((forecast) => {
            const serialized = this.serialize(forecast);
            forecastsObj[serialized.date] = forecast;
        });
        return this.storage.setAll(forecastsObj)
        .then(() => {
            return forecasts;
        })

    }

    private canStoreDate(date: Date): boolean {
        const datesToSave = this.cacheableDates();
        const minDate = datesToSave[0];
        const maxDate = datesToSave[datesToSave.length - 1];
        if (minDate <= date && maxDate >= date) {
            return true;
        } else {
            return false;
        }
    }

    private cacheableDates(): Array<Date> {
        return this.dateFactory.getCurrentWeek();
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
