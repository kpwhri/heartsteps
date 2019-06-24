import { NgModule } from '@angular/core';
import { WeatherComponent } from './weather.component';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';

@NgModule({
    declarations: [
        WeatherComponent
    ],
    exports: [
        WeatherComponent
    ],
    imports: [
        InfrastructureModule
    ]
})
export class WeatherModule {}
