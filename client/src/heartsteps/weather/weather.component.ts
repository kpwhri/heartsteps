import { Component, Input, OnDestroy, ElementRef, Renderer2 } from "@angular/core";
import { WeatherService } from "./weather.service";
import { Subscription } from "rxjs";

const CATEGORY_TO_ICON_MAP:any = {
    cloudy: 'cloudy',
    'partially-cloudy': 'partly-cloudy',
    rain: 'rain',
    snow: 'snow',
    clear: 'sunny',
    thunderstorm: 'thunderstorm',
    windy: 'windy'
};
const DEFAULT_ICON = 'partly-cloudy';


@Component({
    selector: 'heartsteps-weather',
    templateUrl: './weather.component.html'
})
export class WeatherComponent implements OnDestroy {

    private date: Date;
    private weatherSubscription: Subscription;

    public loading: boolean = true;

    public icon: string;
    public high: number;
    public low: number;

    constructor(
        private weatherService: WeatherService,
        private element: ElementRef,
        private renderer: Renderer2
    ) {}

    ngOnDestroy() {
        this.unwatchWeather();
    }

    @Input('date')
    set setDate(date: Date) {
        if(date) {
            this.date = date;
            this.unwatchWeather();
            this.watchWeather();
        }
    }

    private setIcon(category:string) {
        if (this.icon) {
            this.renderer.removeClass(this.element.nativeElement, this.icon);
        }
        this.icon = CATEGORY_TO_ICON_MAP[category];
        if(!this.icon) {
            this.icon = DEFAULT_ICON
        }
        this.renderer.addClass(this.element.nativeElement, this.icon);
    }

    private watchWeather() {
        if (this.date) {
            this.weatherSubscription = this.weatherService.watch(this.date)
            .subscribe((dailyWeather) => {
                this.loading = false;
                this.setIcon(dailyWeather.category);
                this.high = dailyWeather.high;
                this.low = dailyWeather.low;
            })
        }
    }

    private unwatchWeather() {
        if(this.weatherSubscription) {
            this.weatherSubscription.unsubscribe();
        }
    }

}
