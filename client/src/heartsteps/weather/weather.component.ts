import { Component, Input } from "@angular/core";


@Component({
    selector: 'heartsteps-weather',
    templateUrl: './weather.component.html'
})
export class WeatherComponent {

    @Input('date') date:Date;

    constructor() {
        console.log('Weather component');
        console.log(this.date);
    }

}
