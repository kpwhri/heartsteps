import { NgModule } from '@angular/core';
import { WeatherComponent } from './weather.component';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { WeatherService } from './weather.service';

@NgModule({
    declarations: [
        WeatherComponent
    ],
    exports: [
        WeatherComponent
    ],
    imports: [
        InfrastructureModule
    ],
    providers: [
        WeatherService
    ]
})
export class WeatherModule {}
