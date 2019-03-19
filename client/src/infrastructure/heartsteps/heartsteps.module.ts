import { NgModule } from "@angular/core";
import { InfrastructureModule } from "@infrastructure/infrastructure.module";
import { AnalyticsService } from "./analytics.service";


@NgModule({
    imports: [
        InfrastructureModule
    ],
    providers: [
        AnalyticsService
    ]
})
export class HeartstepsInfrastructureModule {}
