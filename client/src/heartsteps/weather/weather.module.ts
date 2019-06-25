import { NgModule } from '@angular/core';
import { WeatherComponent } from './weather.component';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { WeatherService } from './weather.service';
import { BrowserModule } from '@angular/platform-browser';

@NgModule({
    declarations: [
        WeatherComponent
    ],
    exports: [
        WeatherComponent
    ],
    imports: [
        BrowserModule,
        InfrastructureModule
    ],
    providers: [
        WeatherService
    ]
})
export class WeatherModule {}
