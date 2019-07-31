import { Injectable } from "@angular/core";
import { WeatherService } from "@heartsteps/weather/weather.service";

@Injectable()
export class BackgroundService{

    constructor(
        private weatherService: WeatherService
    ) {}

    public updateCache() {
        this.weatherService.updateCache()
    }
}